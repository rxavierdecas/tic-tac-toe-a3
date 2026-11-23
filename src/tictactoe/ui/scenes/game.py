"""Tela principal da partida: tabuleiro, HUD, entrada dos jogadores e efeitos."""

from __future__ import annotations

import math

import pygame

from tictactoe import config
from tictactoe.core.vector2d import Vector2D
from tictactoe.graphics.coords import BoardLayout
from tictactoe.graphics.effects import ShakeEffect, WinLineEffect
from tictactoe.graphics.particles import ParticleSystem
from tictactoe.graphics.shapes import AnimatedSymbol, GridRenderer
from tictactoe.model.game_engine import GameEngine, GameState, MoveResult
from tictactoe.model.player import Player
from tictactoe.ui.scenes.base import Scene, draw_background
from tictactoe.ui.scenes.game_over import MENU, REMATCH, GameOverPanel
from tictactoe.ui.widgets import draw_text

# Teclas 1–9 seguem o layout do teclado numérico (7 8 9 no topo, 1 2 3 embaixo).
NUMBER_KEYS = {
    **{getattr(pygame, f"K_{n}"): n for n in range(1, 10)},
    **{getattr(pygame, f"K_KP{n}"): n for n in range(1, 10)},
}


def key_to_cell(number: int) -> tuple[int, int]:
    """Converte 1–9 (layout numpad) em (linha, coluna)."""
    index = number - 1
    return 2 - index // 3, index % 3


def format_time(seconds: float) -> str:
    total = int(seconds)
    return f"{total // 60:02d}:{total % 60:02d}"


class GameScene(Scene):
    """Conduz a partida e traduz eventos do motor de regras em feedback visual."""

    def __init__(self, app, engine: GameEngine) -> None:
        super().__init__(app)
        self.engine = engine
        self.layout = BoardLayout(config.BOARD_ORIGIN, config.BOARD_SIZE)
        self.grid = GridRenderer(self.layout)
        self.particles = ParticleSystem()
        self.shake = ShakeEffect()
        self.symbols: dict[tuple[int, int], AnimatedSymbol] = {}
        self.win_effect: WinLineEffect | None = None
        self.end_timer = 0.0
        self.game_over: GameOverPanel | None = None
        self.hover_cell: tuple[int, int] | None = None
        self.time = 0.0
        self._cell_layer = pygame.Surface(
            (round(self.layout.cell_size),) * 2, pygame.SRCALPHA
        )

    # ------------------------------------------------------------- ciclo de vida
    def reset_visuals(self) -> None:
        self.symbols.clear()
        self.particles.clear()
        self.win_effect = None
        self.end_timer = 0.0
        self.game_over = None

    def restart_round(self) -> None:
        self.engine.restart()
        self.reset_visuals()

    def rematch(self) -> None:
        self.engine.rematch()
        self.reset_visuals()

    def go_to_menu(self) -> None:
        from tictactoe.ui.scenes.menu import MenuScene  # import tardio: evita ciclo

        p1, p2 = self.engine.players
        self.app.change_scene(MenuScene(self.app, p1.name, p2.name))

    # ------------------------------------------------------------------ entrada
    def handle_event(self, event) -> None:
        if self.game_over is not None:
            action = self.game_over.handle_event(event)
            if action == REMATCH:
                self.rematch()
            elif action == MENU:
                self.go_to_menu()
            return
        if event.type == pygame.MOUSEMOTION:
            self.hover_cell = self.layout.cell_from_screen(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            cell = self.layout.cell_from_screen(event.pos)
            if cell is not None:
                self.try_move(*cell)
        elif event.type == pygame.KEYDOWN:
            if event.key in NUMBER_KEYS:
                self.try_move(*key_to_cell(NUMBER_KEYS[event.key]))
            elif event.key == pygame.K_p:
                self.engine.toggle_pause()
            elif event.key == pygame.K_ESCAPE:
                if self.engine.state is GameState.PAUSED:
                    self.go_to_menu()
                elif not self.engine.is_over:
                    self.engine.toggle_pause()
                else:
                    self.go_to_menu()
            elif event.key == pygame.K_r:
                self.restart_round()

    def try_move(self, row: int, col: int) -> MoveResult:
        """Envia a jogada ao motor de regras e dispara o feedback visual."""
        player = self.engine.current_player
        result = self.engine.play(row, col)
        if result.accepted:
            self.symbols[(row, col)] = AnimatedSymbol(player.symbol, row, col, player.color)
            center = self.layout.cell_center(row, col)
            self.particles.emit(center, 14, player.color, speed=(40, 160), life=(0.3, 0.6),
                                size=(2, 4))
        if result is MoveResult.WIN:
            self.win_effect = WinLineEffect(
                self.layout, self.engine.winning_line, player.color, self.particles
            )
        elif result is MoveResult.DRAW:
            for (r, c) in self.symbols:
                self.particles.emit(self.layout.cell_center(r, c), 18, config.COLOR_DRAW,
                                    speed=(60, 220), life=(0.5, 1.0))
        elif result is MoveResult.INVALID_OCCUPIED:
            self.shake.trigger((row, col))
        return result

    # ------------------------------------------------------------------ update
    def update(self, dt: float) -> None:
        self.time += dt
        if self.engine.state is GameState.PAUSED:
            return
        self.engine.tick(dt)
        self.grid.update(dt)
        self.shake.update(dt)
        for symbol in self.symbols.values():
            symbol.update(dt)
        # A linha vencedora só começa depois que o último símbolo terminou de ser traçado.
        if self.win_effect is not None and self._last_symbol_finished():
            self.win_effect.update(dt)
            for cell in self.engine.winning_line:
                self.symbols[cell].highlight = self.win_effect.pulse if self.win_effect.closed else 0
        self.particles.update(dt)
        if self.engine.is_over:
            self.end_timer += dt
            if self.game_over is None and self._ready_for_game_over():
                self.game_over = GameOverPanel(self.engine)
        if self.game_over is not None:
            self.game_over.update(dt)

    def _ready_for_game_over(self) -> bool:
        """Exibe o painel após o atraso e, na vitória, após o fechamento da linha."""
        if self.end_timer < config.GAME_OVER_DELAY:
            return False
        return self.win_effect is None or (self.win_effect.closed and self.win_effect.shockwave.finished)

    def _last_symbol_finished(self) -> bool:
        last = self.engine.last_move
        return last is None or last not in self.symbols or self.symbols[last].stroke.finished

    # -------------------------------------------------------------------- draw
    def draw(self, surface) -> None:
        draw_background(surface)
        self.draw_hud(surface)
        self.draw_board(surface)
        self.particles.draw(surface)
        draw_text(surface, "Mouse ou teclas 1–9: jogar   ·   P: pausar   ·   R: reiniciar   ·   ESC: menu",
                  config.FONT_SIZE_SMALL - 4, config.COLOR_TEXT_DIM,
                  center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT - 22))
        if self.engine.state is GameState.PAUSED:
            self.draw_pause(surface)
        if self.game_over is not None:
            self.game_over.draw(surface)

    def draw_board(self, surface) -> None:
        x, y, w, h = self.layout.board_rect()
        panel = pygame.Rect(x - 20, y - 20, w + 40, h + 40)
        pygame.draw.rect(surface, (14, 15, 26), panel.move(0, 8), border_radius=24)
        pygame.draw.rect(surface, config.COLOR_BG_ACCENT, panel, border_radius=24)

        self._draw_cell_feedback(surface)
        self.grid.draw(surface)
        for cell, symbol in self.symbols.items():
            offset = self.shake.offset if self.shake.cell == cell else Vector2D()
            symbol.draw(surface, self.layout, offset)
        if self.win_effect is not None and self.win_effect.trace.started:
            self.win_effect.draw(surface)

    def _draw_cell_feedback(self, surface) -> None:
        """Realce de hover (cor do jogador da vez) e flash de jogada inválida."""
        layer = self._cell_layer
        if self.shake.active and self.shake.cell is not None:
            alpha = int(120 * (1 - self.shake.time / self.shake.duration))
            layer.fill((0, 0, 0, 0))
            pygame.draw.rect(layer, (*config.COLOR_INVALID, alpha), layer.get_rect(), border_radius=12)
            x, y, _, _ = self.layout.cell_rect(*self.shake.cell)
            surface.blit(layer, (x + round(self.shake.offset.x), y))
        cell = self.hover_cell
        if (cell is not None and self.engine.state is GameState.PLAYING
                and self.engine.board.is_valid_move(*cell)):
            pulse = 0.5 + 0.5 * math.sin(self.time * 4.2)
            layer.fill((0, 0, 0, 0))
            color = self.engine.current_player.color
            pygame.draw.rect(layer, (*color, int(25 + 25 * pulse)), layer.get_rect(), border_radius=12)
            x, y, _, _ = self.layout.cell_rect(*cell)
            surface.blit(layer, (x, y))

    def draw_hud(self, surface) -> None:
        p1, p2 = self.engine.players
        self._player_card(surface, p1, pygame.Rect(30, 24, 230, 110))
        self._player_card(surface, p2, pygame.Rect(config.WINDOW_WIDTH - 260, 24, 230, 110))

        cx = config.WINDOW_WIDTH // 2
        draw_text(surface, format_time(self.engine.elapsed), config.FONT_SIZE_LARGE,
                  config.COLOR_TEXT, center=(cx, 50))
        draw_text(surface, f"Partida {self.engine.round}   ·   Velhas: {self.engine.draws}",
                  config.FONT_SIZE_SMALL, config.COLOR_TEXT_DIM, center=(cx, 86))
        if not self.engine.is_over:
            current = self.engine.current_player
            draw_text(surface, f"Vez de {current.name} ({current.symbol})", config.FONT_SIZE_MEDIUM,
                      current.color, center=(cx, 122))

    def _player_card(self, surface, player: Player, rect: pygame.Rect) -> None:
        active = self.engine.current_player is player and not self.engine.is_over
        winner = self.engine.winner is player
        pygame.draw.rect(surface, (14, 15, 26), rect.move(0, 6), border_radius=16)
        pygame.draw.rect(surface, config.COLOR_BG_ACCENT, rect, border_radius=16)
        if active or winner:
            pulse = 0.5 + 0.5 * math.sin(self.time * 3.5)
            width = 3 + round(2 * pulse)
            pygame.draw.rect(surface, player.color, rect, width=width, border_radius=16)
        else:
            pygame.draw.rect(surface, config.COLOR_GRID, rect, width=2, border_radius=16)
        draw_text(surface, player.symbol, config.FONT_SIZE_TITLE, player.color,
                  center=(rect.x + 44, rect.centery))
        draw_text(surface, player.name, config.FONT_SIZE_SMALL + 2, config.COLOR_TEXT,
                  midleft=(rect.x + 84, rect.y + 36))
        draw_text(surface, f"{player.score} {'vitória' if player.score == 1 else 'vitórias'}", config.FONT_SIZE_MEDIUM, config.COLOR_TEXT,
                  midleft=(rect.x + 84, rect.y + 74))

    def draw_pause(self, surface) -> None:
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill(config.COLOR_OVERLAY)
        surface.blit(overlay, (0, 0))
        cx, cy = config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2
        draw_text(surface, "PAUSADO", config.FONT_SIZE_TITLE, config.COLOR_TEXT, center=(cx, cy - 30))
        draw_text(surface, "P: continuar   ·   ESC: voltar ao menu", config.FONT_SIZE_SMALL,
                  config.COLOR_TEXT_DIM, center=(cx, cy + 30))
