"""Matrizes 3x3 em coordenadas homogêneas para transformações 2D.

Um ponto (x, y) é representado como o vetor coluna [x, y, 1]^T, o que
permite expressar translação, rotação e escala como multiplicações de
matrizes e compô-las em uma única matriz:

    M = T · R · S     (aplica escala, depois rotação, depois translação)
"""

from __future__ import annotations

import math
from collections.abc import Iterable

from tictactoe.core.vector2d import Vector2D

Rows = tuple[tuple[float, float, float], ...]


class Matrix3:
    """Matriz 3x3 imutável para transformações afins 2D."""

    __slots__ = ("_m",)

    def __init__(self, rows: Iterable[Iterable[float]]):
        m = tuple(tuple(float(v) for v in row) for row in rows)
        if len(m) != 3 or any(len(row) != 3 for row in m):
            raise ValueError("Matrix3 precisa de exatamente 3x3 elementos")
        self._m: Rows = m

    # ------------------------------------------------------------------ fábricas
    @staticmethod
    def identity() -> Matrix3:
        return Matrix3(((1, 0, 0), (0, 1, 0), (0, 0, 1)))

    @staticmethod
    def translation(tx: float, ty: float) -> Matrix3:
        """Matriz de translação por (tx, ty)."""
        return Matrix3(((1, 0, tx), (0, 1, ty), (0, 0, 1)))

    @staticmethod
    def rotation(angle: float) -> Matrix3:
        """Matriz de rotação em torno da origem (ângulo em radianos).

        Como o eixo Y da tela aponta para baixo, ângulos positivos giram
        visualmente no sentido horário.
        """
        c, s = math.cos(angle), math.sin(angle)
        return Matrix3(((c, -s, 0), (s, c, 0), (0, 0, 1)))

    @staticmethod
    def scale(sx: float, sy: float | None = None) -> Matrix3:
        """Matriz de escala (uniforme quando sy é omitido)."""
        if sy is None:
            sy = sx
        return Matrix3(((sx, 0, 0), (0, sy, 0), (0, 0, 1)))

    @staticmethod
    def trs(position: Vector2D, angle: float = 0.0, scale: float = 1.0) -> Matrix3:
        """Atalho para a composição clássica T · R · S."""
        return (
            Matrix3.translation(position.x, position.y)
            @ Matrix3.rotation(angle)
            @ Matrix3.scale(scale)
        )

    # ---------------------------------------------------------------- operações
    def __matmul__(self, other: Matrix3) -> Matrix3:
        """Produto matricial (composição de transformações)."""
        a, b = self._m, other._m
        return Matrix3(
            tuple(
                sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)
            )
            for i in range(3)
        )

    def apply(self, point: Vector2D) -> Vector2D:
        """Transforma um ponto (w = 1, sofre translação)."""
        m = self._m
        return Vector2D(
            m[0][0] * point.x + m[0][1] * point.y + m[0][2],
            m[1][0] * point.x + m[1][1] * point.y + m[1][2],
        )

    def apply_vector(self, direction: Vector2D) -> Vector2D:
        """Transforma uma direção (w = 0, ignora translação)."""
        m = self._m
        return Vector2D(
            m[0][0] * direction.x + m[0][1] * direction.y,
            m[1][0] * direction.x + m[1][1] * direction.y,
        )

    def apply_all(self, points: Iterable[Vector2D]) -> list[Vector2D]:
        return [self.apply(p) for p in points]

    def inverse(self) -> Matrix3:
        """Inversa de uma transformação afim (usada para tela → mundo)."""
        (a, b, tx), (c, d, ty), _ = self._m
        det = a * d - b * c
        if det == 0:
            raise ValueError("Matriz singular não possui inversa")
        ia, ib = d / det, -b / det
        ic, id_ = -c / det, a / det
        return Matrix3((
            (ia, ib, -(ia * tx + ib * ty)),
            (ic, id_, -(ic * tx + id_ * ty)),
            (0, 0, 1),
        ))

    @property
    def rows(self) -> Rows:
        return self._m

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Matrix3):
            return NotImplemented
        return all(
            math.isclose(x, y, abs_tol=1e-9)
            for ra, rb in zip(self._m, other._m)
            for x, y in zip(ra, rb)
        )

    def __repr__(self) -> str:
        return f"Matrix3({self._m})"
