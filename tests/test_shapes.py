import math

import pytest

from tictactoe.core.vector2d import Vector2D
from tictactoe.graphics.shapes import o_arc_points, partial_segment, x_strokes


def close(v: Vector2D, x: float, y: float):
    assert v.x == pytest.approx(x, abs=1e-6)
    assert v.y == pytest.approx(y, abs=1e-6)


def test_partial_segment_interpola():
    seg = (Vector2D(0, 0), Vector2D(10, 0))
    assert partial_segment(seg, 0.3)[1] == Vector2D(3, 0)
    assert partial_segment(seg, 2)[1] == Vector2D(10, 0)


def test_x_formado_por_dois_tracos_diagonais_simetricos():
    c = Vector2D(100, 100)
    d = math.sqrt(2) * 10
    (a0, a1), (b0, b1) = x_strokes(c, d)
    # Traço 1 vai de cima-esquerda para baixo-direita (eixo Y para baixo).
    close(a0, 90, 90)
    close(a1, 110, 110)
    # Traço 2 vai de cima-direita para baixo-esquerda.
    close(b0, 110, 90)
    close(b1, 90, 110)


def test_x_escala_reduz_tracos():
    c = Vector2D(0, 0)
    (a0, a1), _ = x_strokes(c, 10, scale=0.5)
    assert (a1 - a0).length() == pytest.approx(10)


def test_o_completo_fecha_o_circulo_e_mantem_raio():
    c = Vector2D(50, 50)
    pts = o_arc_points(c, 20, 1.0, segments=32)
    assert len(pts) == 33
    close(pts[0], 50, 30)
    close(pts[-1], 50, 30)
    for p in pts:
        assert (p - c).length() == pytest.approx(20)


def test_o_parcial_termina_no_angulo_proporcional():
    c = Vector2D(0, 0)
    pts = o_arc_points(c, 10, 0.25, segments=64)
    # Começa no topo (-90°); 1/4 de volta termina à direita (0°).
    close(pts[-1], 10, 0)


def test_o_progresso_zero_tem_um_ponto():
    assert len(o_arc_points(Vector2D(0, 0), 10, 0.0)) == 1
