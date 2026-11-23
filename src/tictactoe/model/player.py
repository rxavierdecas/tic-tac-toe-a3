"""Jogador humano participante da partida."""

from __future__ import annotations

from dataclasses import dataclass

SYMBOL_X = "X"
SYMBOL_O = "O"
VALID_SYMBOLS = (SYMBOL_X, SYMBOL_O)


@dataclass
class Player:
    """Identificação, símbolo, cor e placar acumulado de um jogador."""

    name: str
    symbol: str
    color: tuple[int, int, int] = (255, 255, 255)
    score: int = 0

    def __post_init__(self) -> None:
        if self.symbol not in VALID_SYMBOLS:
            raise ValueError(f"Símbolo inválido: {self.symbol!r}")
        self.name = self.name.strip() or f"Jogador {self.symbol}"

    def add_win(self) -> None:
        """Contabiliza uma vitória no placar."""
        self.score += 1

    def reset_score(self) -> None:
        self.score = 0
