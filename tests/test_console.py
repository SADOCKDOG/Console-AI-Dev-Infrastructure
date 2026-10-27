"""Pruebas unitarias e integradas para la Consola de Gestion Integral de Escritorio."""

import os
import sys
import tempfile
import sqlite3
from pathlib import Path

# Asegurar importacion
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from console.config import load_settings, resolve_db_path
from console.models import init_local_db, LOCAL_SCHEMA_SQL

try:
    import pytest
except ImportError:
    pytest = None


def test_config_loading():
    settings = load_settings()
    assert "organization" in settings
    assert settings["organization"] == "Sdog Farm Software Factory"
    assert "tenant" in settings
    assert settings["tenant"] == "sadogfarm.onmicrosoft.com"
    assert "ports" in settings
    assert settings["ports"]["fcc_server"] == 8082
    assert settings["ports"]["backend_fastapi"] == 8000


def test_schema_initialization():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = Path(tmpdir) / "test_factory.db"
        init_local_db(test_db)
        assert test_db.exists()

        conn = sqlite3.connect(test_db)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = {row[0] for row in cursor.fetchall()}

            assert "tasks" in tables
            assert "task_events" in tables
            assert "audit_logs" in tables
            assert "incidents" in tables
        finally:
            conn.close()


def test_desktop_console_headless_lifecycle():
    try:
        import tkinter
    except ImportError:
        if pytest:
            pytest.skip("Tkinter no esta disponible en este entorno")
        return

    from console.app import DesktopConsoleApp

    app = DesktopConsoleApp()
    app.withdraw()  # Ocultar ventana para ejecucion en pruebas
    try:
        app.update()

        # Probar generacion de informe sin mostrar dialogo bloqueante
        app.export_audit_report(show_dialog=False)

        # Verificar que el informe markdown fue generado en reports/
        reports_dir = ROOT_DIR / "reports"
        generated_reports = list(reports_dir.glob("informe_auditoria_aigrc_*.md"))
        assert len(generated_reports) > 0

        # Probar ping a puerto loopback (inactivo o activo, sin excepcion)
        ok, latency, msg = app._ping_port("127.0.0.1", 65432)
        assert isinstance(ok, bool)
        assert isinstance(latency, float)
    finally:
        app.destroy()


if __name__ == "__main__":
    print("Ejecutando pruebas de la consola...")
    test_config_loading()
    print("1. test_config_loading: PASSED")
    test_schema_initialization()
    print("2. test_schema_initialization: PASSED")
    test_desktop_console_headless_lifecycle()
    print("3. test_desktop_console_headless_lifecycle: PASSED")
    print("Todas las pruebas pasaron satisfactoriamente.")
