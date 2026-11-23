import pytest

from tictactoe.model.player import Player


def test_add_win_incrementa_placar():
    p = Player("Ana", "X")
    p.add_win()
    p.add_win()
    assert p.score == 2
    p.reset_score()
    assert p.score == 0


def test_nome_vazio_recebe_padrao():
    assert Player("   ", "O").name == "Jogador O"


def test_simbolo_invalido():
    with pytest.raises(ValueError):
        Player("Ana", "Z")
