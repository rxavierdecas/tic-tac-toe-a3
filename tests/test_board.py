import pytest

from tictactoe.model.board import WIN_LINES, Board


def fill(board: Board, layout: str) -> None:
    """Preenche o tabuleiro a partir de 9 caracteres ('X', 'O' ou '.')."""
    for i, ch in enumerate(layout.replace(" ", "")):
        if ch != ".":
            board.place(i // 3, i % 3, ch)


def test_existem_8_linhas_vencedoras():
    assert len(WIN_LINES) == 8
    assert len(set(WIN_LINES)) == 8


def test_tabuleiro_novo_vazio():
    b = Board()
    assert len(b.empty_cells()) == 9
    assert b.winner() is None
    assert not b.is_full()


def test_jogada_em_casa_ocupada_e_rejeitada():
    b = Board()
    assert b.place(1, 1, "X")
    assert not b.place(1, 1, "O")
    assert b.get(1, 1) == "X"


def test_jogada_fora_do_tabuleiro_e_rejeitada():
    b = Board()
    assert not b.is_valid_move(3, 0)
    assert not b.place(-1, 0, "X")


def test_simbolo_invalido_lanca_erro():
    with pytest.raises(ValueError):
        Board().place(0, 0, "Z")


@pytest.mark.parametrize(
    "layout, line",
    [
        ("XXX ... ...", ((0, 0), (0, 1), (0, 2))),
        ("... ... OOO", ((2, 0), (2, 1), (2, 2))),
        (".X. .X. .X.", ((0, 1), (1, 1), (2, 1))),
        ("O.. .O. ..O", ((0, 0), (1, 1), (2, 2))),
        ("..X .X. X..", ((0, 2), (1, 1), (2, 0))),
    ],
)
def test_vitoria_em_linha_coluna_e_diagonais(layout, line):
    b = Board()
    fill(b, layout)
    symbol, win_line = b.winner()
    assert win_line == line
    assert symbol in "XO"


def test_velha():
    b = Board()
    fill(b, "XOX XOO OXX")
    assert b.is_full()
    assert b.winner() is None
    assert b.is_draw()


def test_tabuleiro_cheio_com_vitoria_nao_e_velha():
    b = Board()
    fill(b, "XXX OOX XOO")
    assert b.is_full()
    assert not b.is_draw()


def test_reset_limpa_tabuleiro():
    b = Board()
    fill(b, "XOX ... ...")
    b.reset()
    assert len(b.empty_cells()) == 9
