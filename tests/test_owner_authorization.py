"""Ejercicios locales de autorización. Solo se usan HTTP loopback y SQLite temporal."""
import hashlib
import json
import sqlite3
from contextlib import closing
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from unittest.mock import Mock
from uuid import uuid4

import pytest

from console import app
from console.models import init_local_db
from console.owner_auth_client import OwnerAuthorizationClient, OwnerAuthorizationClientError
from console.owner_signer import AUTH_NAMESPACE, REVOKE_NAMESPACE, canonical_json


@pytest.fixture
def operator(tmp_path, monkeypatch):
    db = tmp_path / "task.db"
    init_local_db(db)
    with closing(sqlite3.connect(db)) as conn, conn:
        conn.execute("INSERT INTO tasks(id,title,status) VALUES ('t','Demo','REVIEW')")
        conn.execute("INSERT INTO task_events(task_id,event_type,payload) VALUES ('t','PULL_REQUEST_PUBLISHED',?)",
                     (json.dumps({"pr_url": "https://github.com/example/farm/pull/12"}),))
    monkeypatch.setattr(app, "DB_PATH", db)
    monkeypatch.setattr(app, "messagebox", Mock())
    monkeypatch.setenv("OWNER_AUTH_FIDO_KEY_HANDLE", str(tmp_path / "synthetic"))
    monkeypatch.setattr(app, "sign_owner_payload", Mock(return_value="synthetic signature"))
    ui = object.__new__(app.DesktopConsoleApp)
    ui.selected_task_id = "t"
    ui._review_owner_pr_snapshot = Mock(return_value=True)
    ui._confirm_owner_signed_payload = Mock(return_value="a" * 12)
    ui.load_tasks = Mock()
    ui.show_task_details = Mock()
    return ui


@pytest.fixture
def factory(operator):
    calls = []
    context = dict(repository="example/farm", pr_number=12, head_sha="a" * 40,
                   base_ref="main", base_sha="b" * 40, diff_sha256="c" * 64)
    authorization = dict(context, authorization_id=str(uuid4()), task_id="t", key_id="test-key",
                         github_login="owner", signer_identity="owner", decision="AUTHORIZE_MERGE",
                         scope={"operation": "MERGE", "allowed_files": ["file.txt"], "allow_agent_execution": False})
    review = dict(context, files=["file.txt"], file_details=[{"filename": "file.txt", "patch": "demo"}])
    routes = {
        "review-context": review, "prepare": None, "owner-authorizations": {"authorization_id": authorization["authorization_id"], "state": "ACTIVE"},
        "history": [dict(authorization, state="ACTIVE")], "by-pr": authorization,
        "revoke": {"state": "REVOKED", "authorization_id": authorization["authorization_id"]},
    }

    class Handler(BaseHTTPRequestHandler):
        def handle_request(self):
            action = self.path.split("?")[0].rsplit("/", 1)[-1]
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"]))) if self.command == "POST" else None
            calls.append((self.command, action, body))
            response = routes[action]
            if action == "prepare" and response is None:
                content = canonical_json(authorization)
                response = dict(payload=authorization, canonical_payload=content.decode(),
                                payload_sha256=hashlib.sha256(content).hexdigest())
            self.send_response(503 if response is None else 200)
            self.end_headers()
            self.wfile.write(json.dumps(response or {"detail": "disabled"}).encode())

        do_GET = do_POST = handle_request

        def log_message(self, *args):
            pass

    with HTTPServer(("127.0.0.1", 0), Handler) as server:
        operator.settings = {"endpoints": {"backend_fastapi": f"http://127.0.0.1:{server.server_port}"}}
        worker = Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            yield calls, authorization, routes
        finally:
            server.shutdown()
            worker.join()


def assert_review_preserved():
    with closing(sqlite3.connect(app.DB_PATH)) as conn:
        assert conn.execute("SELECT status FROM tasks").fetchone() == ("REVIEW",)
        assert conn.execute("SELECT event_type FROM task_events").fetchall() == [("PULL_REQUEST_PUBLISHED",)]
        assert conn.execute("SELECT count(*) FROM audit_logs").fetchone() == (0,)


def test_authorize_history_and_revoke(operator, factory):
    calls, auth, _ = factory
    operator.approve_selected_task()
    assert calls[-1][1] == "owner-authorizations"
    app.messagebox.showerror.assert_not_called()
    assert calls[-1][2]["payload"] == auth
    assert app.sign_owner_payload.call_args.kwargs["namespace"] == AUTH_NAMESPACE
    operator.show_owner_authorization_status()
    assert calls[-1][1] == "history"
    operator.revoke_owner_authorization()
    assert calls[-1][1] == "revoke"
    assert calls[-1][2]["payload"]["issued_at"].endswith("Z")
    assert calls[-1][2]["payload"]["authorization_id"] == auth["authorization_id"]
    assert app.sign_owner_payload.call_args.kwargs["namespace"] == REVOKE_NAMESPACE
    assert_review_preserved()


@pytest.mark.parametrize("failure", ["disabled", "changed-head", "wrong-scope", "cancel", "wrong-repo", "wrong-digest"])
def test_approval_stops_before_signing(operator, factory, failure):
    calls, auth, routes = factory
    if failure == "disabled":
        routes["review-context"] = None
    elif failure == "changed-head":
        auth["head_sha"] = "d" * 40
    elif failure == "wrong-scope":
        auth["scope"]["allow_agent_execution"] = True
    elif failure == "cancel":
        operator._confirm_owner_signed_payload.return_value = None
    elif failure == "wrong-repo":
        routes["review-context"]["repository"] = "example/other"
    else:
        routes["prepare"] = dict(payload=auth, canonical_payload=canonical_json(auth).decode(), payload_sha256="bad")
    operator.approve_selected_task()
    assert all(action != "owner-authorizations" for _, action, _ in calls)
    app.sign_owner_payload.assert_not_called()
    assert_review_preserved()


@pytest.mark.parametrize("skip", [False, True])
def test_promotion_cannot_execute(operator, monkeypatch, skip):
    monkeypatch.setattr(app.subprocess, "run", Mock(side_effect=AssertionError("unexpected subprocess")))
    assert operator.promote_selected_task_to_production(skip_confirm=skip) is False
    app.subprocess.run.assert_not_called()
    assert_review_preserved()


def test_conflicting_or_missing_pr_link_cannot_authorize(operator, factory, monkeypatch):
    calls, _, _ = factory
    monkeypatch.setattr(app.subprocess, "run", Mock(side_effect=AssertionError("inferred PR")))
    with closing(sqlite3.connect(app.DB_PATH)) as conn, conn:
        conn.execute("UPDATE task_events SET payload=?",
                     (json.dumps({"pr_url": "https://github.com/example/farm/pull/12", "pr_number": 13}),))
    operator.approve_selected_task()
    assert calls == []
    with closing(sqlite3.connect(app.DB_PATH)) as conn, conn:
        conn.execute("DELETE FROM task_events")
    operator.approve_selected_task()
    assert calls == []
    app.subprocess.run.assert_not_called()


def test_owner_api_requires_loopback():
    with pytest.raises(OwnerAuthorizationClientError):
        OwnerAuthorizationClient("https://example.org")
