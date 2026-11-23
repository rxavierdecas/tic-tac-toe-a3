"""Sistema de partículas 2D (integração de Euler com gravidade e arrasto).

Cada partícula guarda posição e velocidade como vetores; a cada quadro:

    v ← (v + g·dt) · arrasto
    p ← p + v·dt

A opacidade e o tamanho decaem proporcionalmente à vida restante.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame

from tictactoe.core.vector2d import Vector2D

GRAVITY = Vector2D(0, 520)   # px/s², eixo Y da tela aponta para baixo
DRAG = 0.985


@dataclass
class Particle:
    position: Vector2D
    velocity: Vector2D
    life: float
    color: tuple[int, int, int]
    size: float = 4.0

    def __post_init__(self) -> None:
        self.max_life = self.life

    @property
    def alive(self) -> bool:
        return self.life > 0

    @property
    def ratio(self) -> float:
        """Fração de vida restante (1 = recém-criada, 0 = morta)."""
        return max(0.0, self.life / self.max_life)

    def update(self, dt: float, gravity: Vector2D = GRAVITY, drag: float = DRAG) -> None:
        self.velocity = (self.velocity + gravity * dt) * drag
        self.position = self.position + self.velocity * dt
        self.life -= dt


class ParticleSystem:
    """Gerencia emissão, simulação e desenho de partículas."""

    def __init__(self, rng: random.Random | None = None, max_particles: int = 1500) -> None:
        self.particles: list[Particle] = []
        self.rng = rng or random.Random()
        self.max_particles = max_particles
        self._layer = None

    def __len__(self) -> int:
        return len(self.particles)

    def emit(
        self,
        position: Vector2D,
        count: int,
        color,
        speed: tuple[float, float] = (120, 420),
        life: tuple[float, float] = (0.6, 1.3),
        size: tuple[float, float] = (2.5, 6.0),
        angle_range: tuple[float, float] = (0.0, 2 * math.pi),
    ) -> None:
        """Explosão radial a partir de um ponto."""
        r = self.rng
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                return
            direction = Vector2D.from_angle(r.uniform(*angle_range), r.uniform(*speed))
            self.particles.append(
                Particle(position, direction, r.uniform(*life), color, r.uniform(*size))
            )

    def emit_along(self, start: Vector2D, end: Vector2D, count: int, color, **kwargs) -> None:
        """Distribui emissões ao longo de um segmento (ex.: linha vencedora)."""
        for i in range(count):
            t = i / max(1, count - 1)
            self.emit(start.lerp(end, t), 1, color, **kwargs)

    def update(self, dt: float) -> None:
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive]

    def clear(self) -> None:
        self.particles.clear()

    def draw(self, surface) -> None:
        if not self.particles:
            return
        size = surface.get_size()
        if self._layer is None or self._layer.get_size() != size:
            self._layer = pygame.Surface(size, pygame.SRCALPHA)
        layer = self._layer
        layer.fill((0, 0, 0, 0))
        for p in self.particles:
            k = p.ratio
            radius = max(1, round(p.size * (0.4 + 0.6 * k)))
            pygame.draw.circle(layer, (*p.color[:3], int(255 * k)), p.position.to_int_tuple(), radius)
        surface.blit(layer, (0, 0))
