"""Punto de entrada principal para la Consola de Gestion Integral de Escritorio."""

import sys
from pathlib import Path

# Asegurar que el directorio raiz este en sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from console.app import main

if __name__ == "__main__":
    main()
