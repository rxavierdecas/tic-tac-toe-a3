"""Ponto de entrada do Jogo da Velha: python main.py"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from tictactoe import config  # noqa: E402
from tictactoe.app import App  # noqa: E402
from tictactoe.model.game_engine import GameEngine  # noqa: E402
from tictactoe.model.player import Player  # noqa: E402
from tictactoe.ui.scenes.game import GameScene  # noqa: E402


def main() -> None:
    engine = GameEngine(
        Player("Jogador 1", "X", config.COLOR_X),
        Player("Jogador 2", "O", config.COLOR_O),
    )
    App().run(lambda app: GameScene(app, engine))


if __name__ == "__main__":
    main()
