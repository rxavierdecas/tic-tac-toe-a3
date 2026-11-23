"""Renderização geométrica da grade e dos símbolos X e O.

A geometria é definida em um espaço de modelo local e levada para a tela
por matrizes de transformação (T · R · S). As funções de geometria são puras
(sem Pygame), e as classes de renderização apenas desenham os resultados.

- X: um segmento-base horizontal (-1,0)→(1,0) rotacionado em 45° e 135°.
- O: polígono obtido rotacionando repetidamente o vetor raio por um passo
  angular fixo (matriz de rotação aplicada N vezes).
- Animação de traçado: cada traço é desenhado parcialmente até o ponto
  P(t) = P0 + (P1 - P0)·t.
"""

from __future__ import annotations

import math

import pygame

from tictactoe import config
from tictactoe.core.transform import Matrix3
from tictactoe.core.vector2d import Vector2D
from tictactoe.graphics.animation import Tween, ease_in_out_sine, ease_out_back, ease_out_cubic
from tictactoe.graphics.coords import BoardLayout

Segment = tuple[Vector2D, Vector2D]

BASE_SEGMENT: Segment = (Vector2D(-1, 0), Vector2D(1, 0))
X_ANGLES = (math.pi / 4, 3 * math.pi / 4)   # traço "\" e depois traço "/"
O_SEGMENTS = 64


# ============================================================ geometria pura
def partial_segment(segment: Segment, t: float) -> Segment:
    """Segmento truncado em t ∈ [0, 1] (animação de traçado)."""
    p0, p1 = segment
    return p0, p0.lerp(p1, max(0.0, min(1.0, t)))


def x_strokes(center: Vector2D, half_diagonal: float, scale: float = 1.0) -> list[Segment]:
    """Os dois traços do X transformados para a tela."""
    strokes = []
    for angle in X_ANGLES:
        m = Matrix3.trs(center, angle, half_diagonal * scale)
        strokes.append((m.apply(BASE_SEGMENT[0]), m.apply(BASE_SEGMENT[1])))
    return strokes


def o_arc_points(
    center: Vector2D,
    radius: float,
    progress: float = 1.0,
    segments: int = O_SEGMENTS,
    start_angle: float = -math.pi / 2,
) -> list[Vector2D]:
    """Pontos do arco do O de 0 até `progress` de uma volta completa.

    O vetor raio é rotacionado incrementalmente pela matriz R(Δθ).
    """
    progress = max(0.0, min(1.0, progress))
    step = Matrix3.rotation(2 * math.pi / segments)
    radius_vec = Vector2D.from_angle(start_angle, radius)
    full_steps = int(progress * segments)
    points = [center + radius_vec]
    for _ in range(full_steps):
        radius_vec = step.apply_vector(radius_vec)
        points.append(center + radius_vec)
    remainder = progress * segments - full_steps
    if remainder > 1e-6:
        partial = Matrix3.rotation(remainder * 2 * math.pi / segments)
        points.append(center + partial.apply_vector(radius_vec))
    return points


# ======================================================= primitivas de desenho
def draw_thick_segment(surface, color, p0: Vector2D, p1: Vector2D, width: int) -> None:
    """Linha grossa com pontas arredondadas."""
    a, b = p0.to_int_tuple(), p1.to_int_tuple()
    pygame.draw.line(surface, color, a, b, width)
    radius = width // 2
    pygame.draw.circle(surface, color, a, radius)
    pygame.draw.circle(surface, color, b, radius)


def draw_ring_arc(surface, color, points: list[Vector2D], center: Vector2D, width: int) -> None:
    """Arco grosso como polígono (contorno externo + interno invertido)."""
    if len(points) < 2:
        return
    half = width / 2
    outer, inner = [], []
    for p in points:
        direction = (p - center).normalized()
        outer.append((p + direction * half).to_int_tuple())
        inner.append((p - direction * half).to_int_tuple())
    pygame.draw.polygon(surface, color, outer + inner[::-1])
    radius = round(half)
    pygame.draw.circle(surface, color, points[0].to_int_tuple(), radius)
    pygame.draw.circle(surface, color, points[-1].to_int_tuple(), radius)


def darken(color, factor: float = 0.35):
    return tuple(int(c * factor) for c in color[:3])


# ============================================================== renderizadores
class GridRenderer:
    """Desenha as 4 linhas da grade com traçado animado e escalonado."""

    STAGGER = 0.12

    def __init__(self, layout: BoardLayout) -> None:
        self.layout = layout
        self.tweens = [
            Tween(config.GRID_DRAW_TIME, ease_out_cubic, delay=i * self.STAGGER)
            for i in range(4)
        ]

    def restart(self) -> None:
        for tw in self.tweens:
            tw.reset()

    @property
    def finished(self) -> bool:
        return all(tw.finished for tw in self.tweens)

    def update(self, dt: float) -> None:
        for tw in self.tweens:
            tw.update(dt)

    def draw(self, surface) -> None:
        width = config.GRID_LINE_WIDTH
        for segment, tw in zip(self.layout.grid_lines(), self.tweens):
            if tw.started:
                p0, p1 = partial_segment(segment, tw.value)
                draw_thick_segment(surface, config.COLOR_GRID, p0, p1, width)


class AnimatedSymbol:
    """Um X ou O posicionado numa célula, com traçado e "pop" de escala."""

    def __init__(self, symbol: str, row: int, col: int, color) -> None:
        self.symbol = symbol
        self.row, self.col = row, col
        self.color = color
        self.stroke = Tween(config.SYMBOL_DRAW_TIME, ease_in_out_sine)
        self.pop = Tween(config.SYMBOL_DRAW_TIME * 1.4, ease_out_back)
        self.highlight = 0.0  # 0..1, intensidade do destaque de vitória

    @property
    def finished(self) -> bool:
        return self.stroke.finished and self.pop.finished

    def update(self, dt: float) -> None:
        self.stroke.update(dt)
        self.pop.update(dt)

    def draw(self, surface, layout: BoardLayout, offset: Vector2D = Vector2D()) -> None:
        center = layout.cell_center(self.row, self.col) + offset
        scale = 0.6 + 0.4 * self.pop.value
        scale *= 1.0 + 0.12 * self.highlight
        width = config.SYMBOL_LINE_WIDTH
        color = self._current_color()
        shadow_offset = Vector2D(4, 5)

        if self.symbol == "X":
            half_diag = layout.cell_size * (0.5 - config.SYMBOL_PADDING) * math.sqrt(2)
            strokes = x_strokes(center, half_diag, scale)
            # O primeiro traço ocupa a 1ª metade do tempo, o segundo a 2ª metade.
            t = self.stroke.value
            parts = [min(1.0, t * 2), max(0.0, t * 2 - 1)]
            for (seg, part) in zip(strokes, parts):
                if part <= 0:
                    continue
                p0, p1 = partial_segment(seg, part)
                draw_thick_segment(surface, darken(color), p0 + shadow_offset, p1 + shadow_offset, width)
                draw_thick_segment(surface, color, p0, p1, width)
        else:
            radius = layout.cell_size * (0.5 - config.SYMBOL_PADDING) * scale
            pts = o_arc_points(center, radius, self.stroke.value)
            shadow = [p + shadow_offset for p in pts]
            draw_ring_arc(surface, darken(color), shadow, center + shadow_offset, width)
            draw_ring_arc(surface, color, pts, center, width)

    def _current_color(self):
        if self.highlight <= 0:
            return self.color
        # Mistura com branco para "acender" o símbolo vencedor.
        h = 0.45 * self.highlight
        return tuple(int(c + (255 - c) * h) for c in self.color)
