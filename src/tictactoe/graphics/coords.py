"""Mapeamento entre o sistema de coordenadas do mundo (tabuleiro) e da tela.

Espaço de mundo: o tabuleiro ocupa o quadrado [0, 3] x [0, 3]; a célula
(linha r, coluna c) cobre x ∈ [c, c+1] e y ∈ [r, r+1]. Uma unidade de mundo
equivale a uma célula.

Espaço de tela: pixels da janela, origem no canto superior esquerdo.

    tela  = M · mundo        com  M = T(origem) · S(tamanho_da_célula)
    mundo = M⁻¹ · tela       (usado no hit-test do mouse)
"""

from __future__ import annotations

import math
from typing import Optional

from tictactoe.core.transform import Matrix3
from tictactoe.core.vector2d import Vector2D
from tictactoe.model.board import SIZE


class BoardLayout:
    """Converte coordenadas de mundo do tabuleiro para pixels e vice-versa."""

    def __init__(self, origin: tuple[float, float], board_size: float) -> None:
        self.origin = Vector2D(*origin)
        self.board_size = float(board_size)
        self.cell_size = self.board_size / SIZE
        self.world_to_screen = (
            Matrix3.translation(self.origin.x, self.origin.y)
            @ Matrix3.scale(self.cell_size)
        )
        self.screen_to_world = self.world_to_screen.inverse()

    # ------------------------------------------------------------- conversões
    def to_screen(self, world: Vector2D) -> Vector2D:
        return self.world_to_screen.apply(world)

    def to_world(self, screen: Vector2D) -> Vector2D:
        return self.screen_to_world.apply(screen)

    # ------------------------------------------------------------ consultas
    def cell_from_screen(self, pos: tuple[float, float]) -> Optional[tuple[int, int]]:
        """Retorna (linha, coluna) da célula sob o ponto de tela, ou None."""
        world = self.to_world(Vector2D(*pos))
        col, row = math.floor(world.x), math.floor(world.y)
        if 0 <= row < SIZE and 0 <= col < SIZE:
            return row, col
        return None

    def cell_center(self, row: int, col: int) -> Vector2D:
        """Centro da célula em coordenadas de tela."""
        return self.to_screen(Vector2D(col + 0.5, row + 0.5))

    def cell_rect(self, row: int, col: int) -> tuple[int, int, int, int]:
        """Retângulo (x, y, largura, altura) da célula em pixels."""
        top_left = self.to_screen(Vector2D(col, row))
        size = round(self.cell_size)
        return (round(top_left.x), round(top_left.y), size, size)

    def grid_lines(self) -> list[tuple[Vector2D, Vector2D]]:
        """Segmentos (em tela) das 4 linhas internas da grade."""
        lines = []
        for i in range(1, SIZE):
            lines.append((self.to_screen(Vector2D(i, 0)), self.to_screen(Vector2D(i, SIZE))))
        for i in range(1, SIZE):
            lines.append((self.to_screen(Vector2D(0, i)), self.to_screen(Vector2D(SIZE, i))))
        return lines

    def board_rect(self) -> tuple[int, int, int, int]:
        size = round(self.board_size)
        return (round(self.origin.x), round(self.origin.y), size, size)
