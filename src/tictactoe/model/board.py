"""Tabuleiro 3x3 do Jogo da Velha e regras de vitória/empate."""

from __future__ import annotations

from typing import Optional

from tictactoe.model.player import VALID_SYMBOLS

SIZE = 3
Cell = tuple[int, int]
Line = tuple[Cell, Cell, Cell]

# As 8 linhas vencedoras: 3 horizontais, 3 verticais e 2 diagonais.
WIN_LINES: tuple[Line, ...] = (
    *(((r, 0), (r, 1), (r, 2)) for r in range(SIZE)),
    *(((0, c), (1, c), (2, c)) for c in range(SIZE)),
    ((0, 0), (1, 1), (2, 2)),
    ((0, 2), (1, 1), (2, 0)),
)


class Board:
    """Matriz 3x3 de células; cada célula é None, 'X' ou 'O'."""

    def __init__(self) -> None:
        self.cells: list[list[Optional[str]]] = []
        self.reset()

    def reset(self) -> None:
        """Esvazia todas as células."""
        self.cells = [[None] * SIZE for _ in range(SIZE)]

    @staticmethod
    def in_bounds(row: int, col: int) -> bool:
        return 0 <= row < SIZE and 0 <= col < SIZE

    def get(self, row: int, col: int) -> Optional[str]:
        return self.cells[row][col]

    def is_valid_move(self, row: int, col: int) -> bool:
        """Jogada é válida se a célula existe e está vazia."""
        return self.in_bounds(row, col) and self.cells[row][col] is None

    def place(self, row: int, col: int, symbol: str) -> bool:
        """Marca a célula com o símbolo. Retorna False se a jogada for inválida."""
        if symbol not in VALID_SYMBOLS:
            raise ValueError(f"Símbolo inválido: {symbol!r}")
        if not self.is_valid_move(row, col):
            return False
        self.cells[row][col] = symbol
        return True

    def winner(self) -> Optional[tuple[str, Line]]:
        """Retorna (símbolo, linha vencedora) ou None se ninguém venceu."""
        for line in WIN_LINES:
            (r0, c0), (r1, c1), (r2, c2) = line
            symbol = self.cells[r0][c0]
            if symbol is not None and symbol == self.cells[r1][c1] == self.cells[r2][c2]:
                return symbol, line
        return None

    def is_full(self) -> bool:
        return all(cell is not None for row in self.cells for cell in row)

    def is_draw(self) -> bool:
        """Velha: tabuleiro cheio e nenhuma linha completa."""
        return self.is_full() and self.winner() is None

    def empty_cells(self) -> list[Cell]:
        return [
            (r, c) for r in range(SIZE) for c in range(SIZE) if self.cells[r][c] is None
        ]

    def __str__(self) -> str:
        return "\n".join(" ".join(cell or "." for cell in row) for row in self.cells)
