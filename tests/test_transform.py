import math

import pytest

from tictactoe.core.transform import Matrix3
from tictactoe.core.vector2d import Vector2D


def approx_vec(v: Vector2D, x: float, y: float):
    assert v.x == pytest.approx(x, abs=1e-9)
    assert v.y == pytest.approx(y, abs=1e-9)


def test_identidade_nao_altera_ponto():
    approx_vec(Matrix3.identity().apply(Vector2D(3, 7)), 3, 7)


def test_translacao():
    approx_vec(Matrix3.translation(10, -5).apply(Vector2D(1, 1)), 11, -4)


def test_translacao_nao_afeta_direcao():
    approx_vec(Matrix3.translation(10, -5).apply_vector(Vector2D(1, 1)), 1, 1)


def test_rotacao_90_graus():
    approx_vec(Matrix3.rotation(math.pi / 2).apply(Vector2D(1, 0)), 0, 1)


def test_escala_uniforme_e_nao_uniforme():
    approx_vec(Matrix3.scale(2).apply(Vector2D(3, 4)), 6, 8)
    approx_vec(Matrix3.scale(2, 0.5).apply(Vector2D(3, 4)), 6, 2)


def test_composicao_trs_aplica_escala_rotacao_translacao_nessa_ordem():
    m = Matrix3.trs(Vector2D(100, 50), math.pi / 2, 2)
    # (1,0) -> escala (2,0) -> rotaciona (0,2) -> translada (100,52)
    approx_vec(m.apply(Vector2D(1, 0)), 100, 52)


def test_composicao_nao_e_comutativa():
    t = Matrix3.translation(5, 0)
    r = Matrix3.rotation(math.pi / 2)
    assert (t @ r) != (r @ t)


def test_inversa():
    m = Matrix3.trs(Vector2D(30, -20), 0.7, 3)
    assert m @ m.inverse() == Matrix3.identity()
    p = Vector2D(4, 9)
    approx_vec(m.inverse().apply(m.apply(p)), 4, 9)


def test_inversa_de_matriz_singular_falha():
    with pytest.raises(ValueError):
        Matrix3.scale(0).inverse()


def test_tamanho_invalido():
    with pytest.raises(ValueError):
        Matrix3(((1, 0), (0, 1)))
