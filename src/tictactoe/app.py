"""Aplicação: janela, laço principal com taxa de quadros fixa e troca de cenas."""

from __future__ import annotations

from collections.abc import Callable

import pygame

from tictactoe import config
from tictactoe.ui.scenes.base import Scene
from tictactoe.ui.widgets import draw_text

MAX_DT = 1 / 20   # evita saltos grandes de simulação após travamentos


class App:
    """Laço de jogo: eventos → update(dt) → draw → flip, travado em 60 FPS."""

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(config.WINDOW_TITLE)
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.scene: Scene | None = None
        self.running = False
        self.show_fps = False

    def change_scene(self, scene: Scene) -> None:
        self.scene = scene
        scene.on_enter()

    def quit(self) -> None:
        self.running = False

    def run(self, initial_scene: Callable[[App], Scene]) -> None:
        self.change_scene(initial_scene(self))
        self.running = True
        while self.running:
            # clock.tick limita a 60 FPS e retorna o tempo do quadro em ms.
            dt = min(self.clock.tick(config.FPS) / 1000.0, MAX_DT)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_F3:
                    self.show_fps = not self.show_fps
                else:
                    self.scene.handle_event(event)
            self.scene.update(dt)
            self.scene.draw(self.screen)
            if self.show_fps:
                draw_text(self.screen, f"{self.clock.get_fps():.0f} FPS", config.FONT_SIZE_SMALL,
                          config.COLOR_TEXT_DIM, topleft=(10, config.WINDOW_HEIGHT - 26))
            pygame.display.flip()
        pygame.quit()
