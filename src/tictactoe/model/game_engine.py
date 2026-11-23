"""Motor de regras: controla turnos, estados da partida, placar e cronômetro."""

from __future__ import annotations

from enum import Enum, auto
from typing import Optional

from tictactoe.model.board import Board, Line
from tictactoe.model.player import SYMBOL_O, SYMBOL_X, Player


class GameState(Enum):
    PLAYING = auto()
    PAUSED = auto()
    WIN = auto()
    DRAW = auto()


class MoveResult(Enum):
    OK = auto()                  # jogada aceita, partida continua
    WIN = auto()                 # jogada aceita e encerrou com vitória
    DRAW = auto()                # jogada aceita e encerrou em velha
    INVALID_OCCUPIED = auto()    # célula já marcada
    INVALID_OUT_OF_BOUNDS = auto()
    GAME_OVER = auto()           # partida já encerrada
    PAUSED = auto()              # jogo pausado

    @property
    def accepted(self) -> bool:
        return self in (MoveResult.OK, MoveResult.WIN, MoveResult.DRAW)


class GameEngine:
    """Orquestra a partida entre dois jogadores sobre um Board."""

    def __init__(self, player1: Player, player2: Player) -> None:
        if {player1.symbol, player2.symbol} != {SYMBOL_X, SYMBOL_O}:
            raise ValueError("Os jogadores devem usar símbolos distintos (X e O)")
        self.players: tuple[Player, Player] = (player1, player2)
        self.board = Board()
        self.draws = 0
        self.round = 0
        self._starter_index = 0
        self._new_round()

    # ------------------------------------------------------------------ estado
    def _new_round(self) -> None:
        self.board.reset()
        self.state = GameState.PLAYING
        self._current_index = self._starter_index
        self.winner: Optional[Player] = None
        self.winning_line: Optional[Line] = None
        self.last_move: Optional[tuple[int, int]] = None
        self.move_count = 0
        self.elapsed = 0.0
        self.round += 1

    @property
    def current_player(self) -> Player:
        return self.players[self._current_index]

    @property
    def is_over(self) -> bool:
        return self.state in (GameState.WIN, GameState.DRAW)

    def player_by_symbol(self, symbol: str) -> Player:
        return next(p for p in self.players if p.symbol == symbol)

    # ----------------------------------------------------------------- jogadas
    def play(self, row: int, col: int) -> MoveResult:
        """Processa a jogada do jogador da vez na célula (row, col)."""
        if self.state is GameState.PAUSED:
            return MoveResult.PAUSED
        if self.is_over:
            return MoveResult.GAME_OVER
        if not Board.in_bounds(row, col):
            return MoveResult.INVALID_OUT_OF_BOUNDS
        if not self.board.place(row, col, self.current_player.symbol):
            return MoveResult.INVALID_OCCUPIED

        self.last_move = (row, col)
        self.move_count += 1
        return self._check_end()

    def _check_end(self) -> MoveResult:
        result = self.board.winner()
        if result is not None:
            symbol, line = result
            self.state = GameState.WIN
            self.winner = self.player_by_symbol(symbol)
            self.winning_line = line
            self.winner.add_win()
            return MoveResult.WIN
        if self.board.is_full():
            self.state = GameState.DRAW
            self.draws += 1
            return MoveResult.DRAW
        self._switch_turn()
        return MoveResult.OK

    def _switch_turn(self) -> None:
        self._current_index = 1 - self._current_index

    # --------------------------------------------------------------- controles
    def toggle_pause(self) -> bool:
        """Alterna entre jogando e pausado. Retorna True se ficou pausado."""
        if self.state is GameState.PLAYING:
            self.state = GameState.PAUSED
        elif self.state is GameState.PAUSED:
            self.state = GameState.PLAYING
        return self.state is GameState.PAUSED

    def restart(self) -> None:
        """Reinicia a partida atual (mesmo jogador inicial, placar mantido)."""
        self.round -= 1
        self._new_round()

    def rematch(self) -> None:
        """Nova partida alternando quem começa; placar acumulado é mantido."""
        self._starter_index = 1 - self._starter_index
        self._new_round()

    def reset_scores(self) -> None:
        for p in self.players:
            p.reset_score()
        self.draws = 0

    def tick(self, dt: float) -> None:
        """Avança o cronômetro apenas enquanto a partida está em andamento."""
        if self.state is GameState.PLAYING:
            self.elapsed += dt
