"""Vetor bidimensional imutável usado em posições, velocidades e direções."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Vector2D:
    """Vetor 2D com as operações de álgebra linear usadas no jogo."""

    x: float = 0.0
    y: float = 0.0

    def __add__(self, other: Vector2D) -> Vector2D:
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector2D) -> Vector2D:
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> Vector2D:
        return Vector2D(self.x * scalar, self.y * scalar)

    __rmul__ = __mul__

    def __neg__(self) -> Vector2D:
        return Vector2D(-self.x, -self.y)

    def dot(self, other: Vector2D) -> float:
        """Produto escalar."""
        return self.x * other.x + self.y * other.y

    def length(self) -> float:
        """Norma euclidiana (módulo) do vetor."""
        return math.hypot(self.x, self.y)

    def normalized(self) -> Vector2D:
        """Vetor unitário na mesma direção (vetor nulo permanece nulo)."""
        size = self.length()
        if size == 0:
            return Vector2D(0.0, 0.0)
        return Vector2D(self.x / size, self.y / size)

    def perpendicular(self) -> Vector2D:
        """Vetor perpendicular (rotação de 90° no sentido anti-horário)."""
        return Vector2D(-self.y, self.x)

    def lerp(self, target: Vector2D, t: float) -> Vector2D:
        """Interpolação linear: P(t) = A + (B - A) * t."""
        return self + (target - self) * t

    @staticmethod
    def from_angle(angle: float, length: float = 1.0) -> Vector2D:
        """Cria um vetor a partir de um ângulo (radianos) e comprimento."""
        return Vector2D(math.cos(angle) * length, math.sin(angle) * length)

    def to_tuple(self) -> tuple[float, float]:
        return (self.x, self.y)

    def to_int_tuple(self) -> tuple[int, int]:
        """Coordenadas arredondadas para pixels de tela."""
        return (round(self.x), round(self.y))
