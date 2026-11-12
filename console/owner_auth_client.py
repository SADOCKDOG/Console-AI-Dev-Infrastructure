"""Minimal loopback client for signed owner PR authorization endpoints."""

from __future__ import annotations

import json
import re
import unicodedata
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener
from typing import Any
from uuid import UUID


class OwnerAuthorizationClientError(RuntimeError):
    pass


def safe_review_text(value: str) -> str:
    """Make GitHub-controlled text inert in the native review dialog."""
    text = re.sub(r"\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\x07]*(?:\x07|\x1b\\))", "[ANSI]", str(value))
    rendered = []
    for char in text:
        category = unicodedata.category(char)
        if char in "\n\t":
            rendered.append(char)
        elif category in {"Cc", "Cf", "Cs"}:
            rendered.append(f"\\u{ord(char):04x}")
        else:
            rendered.append(char)
    return "".join(rendered)


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class OwnerAuthorizationClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000", timeout: float = 20.0):
        endpoint = urlsplit(base_url)
        if (endpoint.scheme != "http" or endpoint.hostname not in {"localhost", "127.0.0.1", "::1"}
                or endpoint.username is not None or endpoint.password is not None
                or endpoint.path.strip("/") or endpoint.query or endpoint.fragment):
            raise OwnerAuthorizationClientError("La autorización requiere la API local de Factory.")
        self.base_url = base_url.rstrip("/")
        self.opener = build_opener(ProxyHandler({}), _NoRedirect())
        self.timeout = timeout

    def request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
        data = None if payload is None else json.dumps(payload, sort_keys=True).encode("utf-8")
        request = Request(
            self.base_url + path,
            data=data,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            method=method.upper(),
        )
        try:
            with self.opener.open(request, timeout=self.timeout) as response:
                parsed = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            try:
                detail = json.loads(exc.read().decode("utf-8")).get("detail", "solicitud denegada")
            except Exception:
                detail = "solicitud denegada"
            raise OwnerAuthorizationClientError(f"API de autorización ({exc.code}): {detail}") from exc
        except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            message = "La respuesta de Factory no está disponible."
            if method == "POST":
                message += " Consulte HISTORIAL antes de reintentar."
            raise OwnerAuthorizationClientError(message) from exc
        if not isinstance(parsed, (dict, list)):
            raise OwnerAuthorizationClientError("La respuesta de Factory es inválida.")
        return parsed

    def review_context(self, repository: str, pr_number: int) -> dict[str, Any]:
        query = urlencode({"repository": repository, "pr_number": pr_number})
        return self.request("GET", f"/api/v1/owner-authorizations/review-context?{query}")

    def prepare(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.request("POST", "/api/v1/owner-authorizations/prepare", payload)

    def authorize(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.request("POST", "/api/v1/owner-authorizations", payload)

    def revoke(self, authorization_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self.request("POST", f"/api/v1/owner-authorizations/{UUID(authorization_id)}/revoke", payload)

    def status(self, authorization_id: str) -> dict[str, Any]:
        return self.request("GET", f"/api/v1/owner-authorizations/{authorization_id}")

    def active_for_pr(self, repository: str, pr_number: int) -> dict[str, Any]:
        query = urlencode({"repository": repository, "pr_number": pr_number})
        return self.request("GET", f"/api/v1/owner-authorizations/by-pr?{query}")

    def history_for_pr(self, repository: str, pr_number: int) -> list[dict[str, Any]]:
        query = urlencode({"repository": repository, "pr_number": pr_number})
        return self.request("GET", f"/api/v1/owner-authorizations/history?{query}")
