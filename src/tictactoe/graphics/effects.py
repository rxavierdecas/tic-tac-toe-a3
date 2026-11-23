"""Efeitos visuais de feedback: linha vencedora com brilho e tremor de jogada inválida."""

from __future__ import annotations

import math

import pygame

from tictactoe import config
from tictactoe.core.vector2d import Vector2D
from tictactoe.graphics.animation import Tween, ease_out_cubic
from tictactoe.graphics.coords import BoardLayout
from tictactoe.graphics.particles import ParticleSystem
from tictactoe.graphics.shapes import partial_segment

Cell = tuple[int, int]

GLOW_LAYERS = ((34, 40), (22, 80), (12, 255))   # (largura, alpha) de fora para dentro
LINE_OVERSHOOT = 0.38                           # extensão além dos centros, em células


class WinLineEffect:
    """Traça a linha vencedora e, ao fechá-la, dispara brilho e partículas.

    Fases:
      1. traçado animado do primeiro ao último centro (interpolação vetorial);
      2. ao completar: explosão de partículas ao longo da linha e nas pontas,
         onda de choque circular (escala crescente) e pulso luminoso contínuo.
    """

    def __init__(
        self,
        layout: BoardLayout,
        cells: tuple[Cell, Cell, Cell],
        color,
        particles: ParticleSystem,
    ) -> None:
        self.cells = cells
        self.color = color
        self.particles = particles
        first, last = layout.cell_center(*cells[0]), layout.cell_center(*cells[-1])
        direction = (last - first).normalized()
        extra = direction * (layout.cell_size * LINE_OVERSHOOT)
        self.start, self.end = first - extra, last + extra
        self.cell_rects = [layout.cell_rect(*c) for c in cells]
        self.trace = Tween(config.WIN_LINE_DRAW_TIME, ease_out_cubic)
        self.shockwave = Tween(0.7, ease_out_cubic)
        self.time = 0.0
        self.closed = False
        self._layer = None

    @property
    def midpoint(self) -> Vector2D:
        return self.start.lerp(self.end, 0.5)

    @property
    def pulse(self) -> float:
        """Oscilação senoidal 0..1 usada no brilho após o fechamento."""
        return 0.5 + 0.5 * math.sin(self.time * 6.0)

    def update(self, dt: float) -> None:
        self.time += dt
        self.trace.update(dt)
        if self.trace.finished and not self.closed:
            self._on_close()
        if self.closed:
            self.shockwave.update(dt)

    def _on_close(self) -> None:
        self.closed = True
        self.particles.emit_along(self.start, self.end, 90, self.color, speed=(60, 360))
        for point in (self.start, self.end):
            self.particles.emit(point, 40, (255, 255, 255), speed=(150, 480), life=(0.4, 0.9))

    def draw(self, surface) -> None:
        size = surface.get_size()
        if self._layer is None or self._layer.get_size() != size:
            self._layer = pygame.Surface(size, pygame.SRCALPHA)
        layer = self._layer
        layer.fill((0, 0, 0, 0))
        glow = self.pulse if self.closed else 0.0

        # Destaque das células vencedoras.
        for rect in self.cell_rects:
            alpha = int(35 + 45 * glow) if self.closed else int(35 * self.trace.value)
            pygame.draw.rect(layer, (*self.color, alpha), rect, border_radius=12)

        # Linha com camadas de brilho (glow) concêntricas.
        p0, p1 = partial_segment((self.start, self.end), self.trace.value)
        for width, alpha in GLOW_LAYERS:
            w = round(width * (1 + 0.25 * glow))
            self._segment(layer, (*self.color, alpha), p0, p1, w)
        self._segment(layer, (255, 255, 255, 230), p0, p1, 4)

        # Onda de choque: anel cujo raio cresce por escala e cuja opacidade cai.
        if self.closed and not self.shockwave.finished:
            k = self.shockwave.value
            radius = max(1, round(40 + 260 * k))
            alpha = int(200 * (1 - k))
            pygame.draw.circle(layer, (*self.color, alpha), self.midpoint.to_int_tuple(), radius, 6)

        surface.blit(layer, (0, 0))

    @staticmethod
    def _segment(layer, color, p0: Vector2D, p1: Vector2D, width: int) -> None:
        a, b = p0.to_int_tuple(), p1.to_int_tuple()
        pygame.draw.line(layer, color, a, b, width)
        pygame.draw.circle(layer, color, a, width // 2)
        pygame.draw.circle(layer, color, b, width // 2)


class ShakeEffect:
    """Deslocamento oscilante amortecido (feedback de jogada inválida).

        offset(t) = A · sin(2π·f·t) · (1 - t/T)
    """

    def __init__(self, duration: float = config.SHAKE_TIME, amplitude: float = 10.0,
                 frequency: float = 22.0) -> None:
        self.duration = duration
        self.amplitude = amplitude
        self.frequency = frequency
        self.time = duration       # começa inativo
        self.cell: Cell | None = None

    def trigger(self, cell: Cell | None = None) -> None:
        self.time = 0.0
        self.cell = cell

    @property
    def active(self) -> bool:
        return self.time < self.duration

    def update(self, dt: float) -> None:
        self.time = min(self.duration, self.time + dt)

    @property
    def offset(self) -> Vector2D:
        if not self.active:
            return Vector2D()
        decay = 1 - self.time / self.duration
        return Vector2D(self.amplitude * math.sin(2 * math.pi * self.frequency * self.time) * decay, 0)
