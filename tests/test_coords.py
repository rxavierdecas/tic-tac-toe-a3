import pytest

from tictactoe.core.vector2d import Vector2D
from tictactoe.graphics.coords import BoardLayout


@pytest.fixture
def layout() -> BoardLayout:
    # Tabuleiro de 300px com origem em (100, 50): cada célula tem 100px.
    return BoardLayout((100, 50), 300)


def test_mundo_para_tela(layout):
    assert layout.to_screen(Vector2D(0, 0)) == Vector2D(100, 50)
    assert layout.to_screen(Vector2D(3, 3)) == Vector2D(400, 350)


def test_tela_para_mundo_e_inversa(layout):
    w = layout.to_world(Vector2D(250, 200))
    assert w.x == pytest.approx(1.5)
    assert w.y == pytest.approx(1.5)


@pytest.mark.parametrize(
    "pos, cell",
    [
        ((101, 51), (0, 0)),
        ((250, 200), (1, 1)),
        ((399, 349), (2, 2)),
        ((350, 60), (0, 2)),
        ((110, 300), (2, 0)),
    ],
)
def test_hit_test_do_mouse(layout, pos, cell):
    assert layout.cell_from_screen(pos) == cell


@pytest.mark.parametrize("pos", [(99, 60), (401, 60), (200, 49), (200, 351)])
def test_clique_fora_do_tabuleiro(layout, pos):
    assert layout.cell_from_screen(pos) is None


def test_centro_da_celula(layout):
    assert layout.cell_center(0, 2) == Vector2D(350, 100)


def test_quatro_linhas_de_grade(layout):
    lines = layout.grid_lines()
    assert len(lines) == 4
    assert lines[0] == (Vector2D(200, 50), Vector2D(200, 350))
