"""Modulo de configuracion y resolucion de entorno para la Consola de Gestion Integral."""

import json
import os
from pathlib import Path
from typing import Any, Dict

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = ROOT_DIR / "config" / "settings.json"
DATA_DIR = ROOT_DIR / "data"
REPORTS_DIR = ROOT_DIR / "reports"


def load_settings() -> Dict[str, Any]:
    """Carga los parametros de configuracion desde el archivo settings.json."""
    default_settings: Dict[str, Any] = {
        "organization": "Sdog Farm Software Factory",
        "tenant": "sadogfarm.onmicrosoft.com",
        "azure_foundry_hub": "Sdog Farm Software Factory",
        "data_boundary": "EU",
        "ports": {
            "fcc_server": 8082,
            "backend_fastapi": 8000,
        },
        "endpoints": {
            "fcc_server": "http://127.0.0.1:8082",
            "backend_fastapi": "http://127.0.0.1:8000",
        },
        "database_path": "",
        "refresh_interval_ms": 5000,
        "default_page_size": 50,
        "theme": "dark_pro",
    }

    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                default_settings.update(loaded)
        except Exception:
            pass

    return default_settings


def resolve_db_path() -> Path:
    """Resuelve la ruta absoluta hacia la base de datos SQLite con jerarquia de prioridades:
    1. Variable de entorno FACTORY_DB_PATH.
    2. Parametro database_path en config/settings.json.
    3. Base de datos del repositorio AutonomousDev adyacente (C:/Users/yo/repo/AutonomousDev/data/factory.db).
    4. Base de datos local en este repositorio (data/factory.db).
    """
    # 1. Variable de entorno
    env_path = os.getenv("FACTORY_DB_PATH")
    if env_path:
        p = Path(env_path).resolve()
        return p

    # 2. Archivo settings.json
    settings = load_settings()
    configured_path = settings.get("database_path", "").strip()
    if configured_path:
        p = Path(configured_path).resolve()
        return p

    # 3. Repositorio adyacente AutonomousDev
    sibling_db = ROOT_DIR.parent / "AutonomousDev" / "data" / "factory.db"
    if sibling_db.exists():
        return sibling_db

    # 4. Fallback local
    return DATA_DIR / "factory.db"
