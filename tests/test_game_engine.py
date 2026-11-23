import pytest

from tictactoe.model.game_engine import GameEngine, GameState, MoveResult
from tictactoe.model.player import Player


@pytest.fixture
def engine() -> GameEngine:
    return GameEngine(Player("Ana", "X"), Player("Bruno", "O"))


def play_all(engine: GameEngine, moves):
    return [engine.play(r, c) for r, c in moves]


def test_x_comeca_e_turnos_alternam(engine):
    assert engine.current_player.symbol == "X"
    assert engine.play(0, 0) is MoveResult.OK
    assert engine.current_player.symbol == "O"
    assert engine.play(1, 1) is MoveResult.OK
    assert engine.current_player.symbol == "X"


def test_jogada_invalida_nao_troca_turno(engine):
    engine.play(0, 0)
    assert engine.play(0, 0) is MoveResult.INVALID_OCCUPIED
    assert engine.current_player.symbol == "O"
    assert engine.play(5, 5) is MoveResult.INVALID_OUT_OF_BOUNDS
    assert engine.current_player.symbol == "O"


def test_vitoria_atualiza_estado_e_placar(engine):
    results = play_all(engine, [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)])
    assert results[-1] is MoveResult.WIN
    assert engine.state is GameState.WIN
    assert engine.winner.name == "Ana"
    assert engine.winning_line == ((0, 0), (0, 1), (0, 2))
    assert engine.players[0].score == 1
    assert engine.players[1].score == 0


def test_jogada_apos_fim_de_jogo_e_rejeitada(engine):
    play_all(engine, [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)])
    assert engine.play(2, 2) is MoveResult.GAME_OVER
    assert engine.board.get(2, 2) is None


def test_velha_incrementa_empates(engine):
    # X O X / X O O / O X X
    moves = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 0), (1, 2), (2, 1), (2, 0), (2, 2)]
    results = play_all(engine, moves)
    assert results[-1] is MoveResult.DRAW
    assert engine.state is GameState.DRAW
    assert engine.draws == 1
    assert engine.winner is None


def test_pausa_bloqueia_jogadas_e_cronometro(engine):
    engine.tick(1.0)
    assert engine.toggle_pause() is True
    assert engine.play(0, 0) is MoveResult.PAUSED
    engine.tick(5.0)
    assert engine.elapsed == pytest.approx(1.0)
    assert engine.toggle_pause() is False
    assert engine.play(0, 0) is MoveResult.OK


def test_cronometro_para_no_fim_de_jogo(engine):
    play_all(engine, [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)])
    engine.tick(3.0)
    assert engine.elapsed == 0.0


def test_revanche_alterna_quem_comeca_e_mantem_placar(engine):
    play_all(engine, [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)])
    engine.rematch()
    assert engine.state is GameState.PLAYING
    assert engine.current_player.symbol == "O"
    assert engine.players[0].score == 1
    assert len(engine.board.empty_cells()) == 9
    assert engine.round == 2


def test_restart_mantem_jogador_inicial(engine):
    engine.play(0, 0)
    engine.restart()
    assert engine.current_player.symbol == "X"
    assert engine.move_count == 0
    assert engine.round == 1


def test_simbolos_repetidos_sao_rejeitados():
    with pytest.raises(ValueError):
        GameEngine(Player("A", "X"), Player("B", "X"))


def test_reset_scores(engine):
    play_all(engine, [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)])
    engine.reset_scores()
    assert engine.players[0].score == 0
    assert engine.draws == 0
