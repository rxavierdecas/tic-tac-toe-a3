"""Ponto de entrada do Jogo da Velha: python main.py"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from tictactoe.app import App  # noqa: E402
from tictactoe.ui.scenes.menu import MenuScene  # noqa: E402


def main() -> None:
    App().run(MenuScene)


if __name__ == "__main__":
    main()
