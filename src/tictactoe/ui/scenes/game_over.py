"""Painel de fim de jogo (vitória ou velha) com opções de revanche e menu."""

from __future__ import annotations

import pygame

from tictactoe import config
from tictactoe.graphics.animation import Tween, ease_out_back, ease_out_cubic
from tictactoe.model.game_engine import GameEngine, GameState
from tictactoe.ui.widgets import Button, draw_text

PANEL_SIZE = (520, 300)
REMATCH = "rematch"
MENU = "menu"


def result_message(engine: GameEngine) -> tuple[str, tuple[int, int, int]]:
    """Título e cor do resultado da partida."""
    if engine.state is GameState.WIN and engine.winner is not None:
        return f"Vitória de {engine.winner.name}!", engine.winner.color
    return "Deu velha!", config.COLOR_DRAW


class GameOverPanel:
    """Overlay que entra com escala ("pop") e fade sobre a tela da partida."""

    def __init__(self, engine: GameEngine) -> None:
        self.engine = engine
        self.fade = Tween(0.35, ease_out_cubic)
        self.pop = Tween(0.45, ease_out_back)
        cx, cy = config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2
        self.rematch_button = Button((cx - 120, cy + 90), (200, 56), "Revanche", accent=config.COLOR_X)
        self.menu_button = Button((cx + 120, cy + 90), (200, 56), "Menu", accent=config.COLOR_O)

    def handle_event(self, event) -> str | None:
        """Retorna REMATCH, MENU ou None conforme a escolha do jogador."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_r, pygame.K_SPACE):
                return REMATCH
            if event.key in (pygame.K_ESCAPE, pygame.K_m):
                return MENU
        if self.rematch_button.handle_event(event):
            return REMATCH
        if self.menu_button.handle_event(event):
            return MENU
        return None

    def update(self, dt: float) -> None:
        self.fade.update(dt)
        self.pop.update(dt)
        self.rematch_button.update(dt)
        self.menu_button.update(dt)

    def draw(self, surface) -> None:
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(150 * self.fade.value)))
        surface.blit(overlay, (0, 0))

        # Painel desenhado em superfície própria e escalado (transformação de escala).
        w, h = PANEL_SIZE
        panel = pygame.Surface((w, h), pygame.SRCALPHA)
        title, color = result_message(self.engine)
        pygame.draw.rect(panel, (*config.COLOR_BG_ACCENT, 245), panel.get_rect(), border_radius=24)
        pygame.draw.rect(panel, color, panel.get_rect(), width=4, border_radius=24)
        draw_text(panel, title, config.FONT_SIZE_LARGE, color, center=(w // 2, 58))
        p1, p2 = self.engine.players
        draw_text(panel, f"{p1.name}  {p1.score}  ×  {p2.score}  {p2.name}", config.FONT_SIZE_MEDIUM,
                  config.COLOR_TEXT, center=(w // 2, 118))
        draw_text(panel, f"Velhas: {self.engine.draws}   ·   Jogadas: {self.engine.move_count}",
                  config.FONT_SIZE_SMALL, config.COLOR_TEXT_DIM, center=(w // 2, 156))
        draw_text(panel, "Enter: revanche   ·   ESC: menu", config.FONT_SIZE_SMALL - 4,
                  config.COLOR_TEXT_DIM, center=(w // 2, h - 22))

        scale = max(0.01, self.pop.value)
        scaled = pygame.transform.smoothscale(panel, (max(1, round(w * scale)), max(1, round(h * scale))))
        scaled.set_alpha(int(255 * self.fade.value))
        rect = scaled.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2))
        surface.blit(scaled, rect)

        if self.pop.finished:
            self.rematch_button.draw(surface)
            self.menu_button.draw(surface)
