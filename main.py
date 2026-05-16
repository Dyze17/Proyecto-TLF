"""
Motor de Patrones — Aplicación principal.

Punto de entrada para la aplicación de detección, validación y
extracción de patrones en texto mediante autómatas finitos (AFD/AFND).

Uso:
    python main.py
"""

import sys
import os

# Ensure the project root is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.app import Application


def main() -> None:
    app = Application()
    app.run()


if __name__ == "__main__":
    main()
