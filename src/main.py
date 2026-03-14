# Responsable: Yajaira Aldana - Líder de Proyecto y Arquitecta

"""Punto de entrada unico de la aplicacion de biblioteca.

Uso esperado para QA:
    python src/main.py
"""

from pathlib import Path
import sys


SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    # Garantiza imports internos como `from models...` y `from ui...`.
    sys.path.insert(0, str(SRC_DIR))

from ui.app import BibliotecaApp


def main() -> None:
    """Inicia la interfaz grafica principal de la biblioteca."""
    app = BibliotecaApp()
    app.mainloop()


if __name__ == "__main__":
    main()
