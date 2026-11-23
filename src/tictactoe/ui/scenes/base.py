"""Classe base das cenas e fundo compartilhado."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from tictactoe import config

if TYPE_CHECKING:
    from tictactoe.app import App

_background_cache: dict[tuple[int, int], pygame.Surface] = {}


def draw_background(surface) -> None:
    """Gradiente vertical (pré-calculado uma vez por resolução)."""
    size = surface.get_size()
    bg = _background_cache.get(size)
    if bg is None:
        bg = pygame.Surface(size)
        top, bottom = config.COLOR_BG, config.COLOR_BG_ACCENT
        h = size[1]
        for y in range(h):
            t = y / max(1, h - 1)
            color = tuple(round(a + (b - a) * t) for a, b in zip(top, bottom))
            pygame.draw.line(bg, color, (0, y), (size[0], y))
        _background_cache[size] = bg
    surface.blit(bg, (0, 0))


class Scene:
    """Interface de uma tela: recebe eventos, atualiza estado e desenha."""

    def __init__(self, app: App) -> None:
        self.app = app

    def on_enter(self) -> None:
        """Chamado quando a cena se torna ativa."""

    def handle_event(self, event) -> None:
        """Processa um evento do Pygame."""

    def update(self, dt: float) -> None:
        """Avança a simulação em `dt` segundos."""

    def draw(self, surface) -> None:
        """Desenha a cena na superfície da janela."""
        draw_background(surface)
