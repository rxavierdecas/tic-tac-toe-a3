import math

import pytest

from tictactoe.core.vector2d import Vector2D


def test_soma_e_subtracao():
    a, b = Vector2D(1, 2), Vector2D(3, -4)
    assert a + b == Vector2D(4, -2)
    assert a - b == Vector2D(-2, 6)


def test_multiplicacao_por_escalar_comutativa():
    v = Vector2D(2, -3)
    assert v * 2 == Vector2D(4, -6)
    assert 2 * v == Vector2D(4, -6)


def test_produto_escalar_e_perpendicular():
    v = Vector2D(3, 4)
    assert v.dot(Vector2D(1, 0)) == 3
    assert v.dot(v.perpendicular()) == 0


def test_comprimento_e_normalizacao():
    v = Vector2D(3, 4)
    assert v.length() == 5
    n = v.normalized()
    assert n.length() == pytest.approx(1.0)
    assert Vector2D(0, 0).normalized() == Vector2D(0, 0)


def test_lerp_extremos_e_meio():
    a, b = Vector2D(0, 0), Vector2D(10, 20)
    assert a.lerp(b, 0) == a
    assert a.lerp(b, 1) == b
    assert a.lerp(b, 0.5) == Vector2D(5, 10)


def test_from_angle():
    v = Vector2D.from_angle(math.pi / 2, 2)
    assert v.x == pytest.approx(0, abs=1e-9)
    assert v.y == pytest.approx(2)


def test_to_int_tuple_arredonda():
    assert Vector2D(1.6, 2.4).to_int_tuple() == (2, 2)
