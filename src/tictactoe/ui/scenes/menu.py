"""Tela de menu inicial: identificação dos jogadores e instruções de controle."""

from __future__ import annotations

import math

import pygame

from tictactoe import config
from tictactoe.core.transform import Matrix3
from tictactoe.core.vector2d import Vector2D
from tictactoe.graphics.shapes import BASE_SEGMENT, X_ANGLES, darken, draw_ring_arc, draw_thick_segment, o_arc_points
from tictactoe.model.game_engine import GameEngine
from tictactoe.model.player import Player
from tictactoe.ui.scenes.base import Scene, draw_background
from tictactoe.ui.widgets import Button, TextInput, draw_text

CONTROLS = (
    "Clique numa casa ou use as teclas 1–9 (layout do teclado numérico)",
    "P pausa  ·  R reinicia a partida  ·  ESC volta ao menu  ·  F3 mostra FPS",
)


class MenuScene(Scene):
    def __init__(self, app, name1: str = "", name2: str = "") -> None:
        super().__init__(app)
        cx = config.WINDOW_WIDTH // 2
        self.inputs = [
            TextInput((cx - 160, 300, 320, 52), name1, accent=config.COLOR_X, placeholder="Jogador 1"),
            TextInput((cx - 160, 410, 320, 52), name2, accent=config.COLOR_O, placeholder="Jogador 2"),
        ]
        self.inputs[0].focused = True
        self.play_button = Button((cx, 540), (240, 60), "Jogar")
        self.quit_button = Button((cx, 615), (240, 52), "Sair", font_size=config.FONT_SIZE_SMALL + 4)
        self.time = 0.0

    def on_enter(self) -> None:
        pygame.key.start_text_input()

    # ------------------------------------------------------------------ ações
    def start_game(self) -> None:
        name1 = self.inputs[0].text.strip() or "Jogador 1"
        name2 = self.inputs[1].text.strip() or "Jogador 2"
        engine = GameEngine(Player(name1, "X", config.COLOR_X), Player(name2, "O", config.COLOR_O))
        from tictactoe.ui.scenes.game import GameScene  # import tardio: evita ciclo

        self.app.change_scene(GameScene(self.app, engine))

    def handle_event(self, event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            first = self.inputs[0].focused
            self.inputs[0].focused, self.inputs[1].focused = not first, first
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.app.quit()
            return
        for field in self.inputs:
            if field.handle_event(event):
                self.start_game()
                return
        if self.play_button.handle_event(event):
            self.start_game()
        elif self.quit_button.handle_event(event):
            self.app.quit()

    def update(self, dt: float) -> None:
        self.time += dt
        for widget in (*self.inputs, self.play_button, self.quit_button):
            widget.update(dt)

    # ------------------------------------------------------------------- draw
    def draw(self, surface) -> None:
        draw_background(surface)
        cx = config.WINDOW_WIDTH // 2
        draw_text(surface, "JOGO DA VELHA", config.FONT_SIZE_TITLE + 8, config.COLOR_TEXT, center=(cx, 110))
        draw_text(surface, "2 jogadores  ·  mesmo computador", config.FONT_SIZE_SMALL,
                  config.COLOR_TEXT_DIM, center=(cx, 165))
        self._draw_logo(surface)

        draw_text(surface, "Jogador 1  (X)", config.FONT_SIZE_SMALL + 2, config.COLOR_X,
                  midleft=(self.inputs[0].rect.x, self.inputs[0].rect.y - 18))
        draw_text(surface, "Jogador 2  (O)", config.FONT_SIZE_SMALL + 2, config.COLOR_O,
                  midleft=(self.inputs[1].rect.x, self.inputs[1].rect.y - 18))
        for widget in (*self.inputs, self.play_button, self.quit_button):
            widget.draw(surface)

        for i, line in enumerate(CONTROLS):
            draw_text(surface, line, config.FONT_SIZE_SMALL - 4, config.COLOR_TEXT_DIM,
                      center=(cx, config.WINDOW_HEIGHT - 52 + i * 22))

    def _draw_logo(self, surface) -> None:
        """X girando (matriz de rotação) e O pulsando (matriz de escala)."""
        size = 46
        # X: os dois traços recebem uma rotação extra que varia com o tempo.
        x_center = Vector2D(150, 115)
        spin = self.time * 0.9
        for angle in X_ANGLES:
            m = Matrix3.trs(x_center, angle + spin, size)
            p0, p1 = m.apply(BASE_SEGMENT[0]), m.apply(BASE_SEGMENT[1])
            draw_thick_segment(surface, darken(config.COLOR_X), p0 + Vector2D(4, 5), p1 + Vector2D(4, 5), 12)
            draw_thick_segment(surface, config.COLOR_X, p0, p1, 12)
        # O: raio escalado por uma oscilação senoidal ("respiração").
        o_center = Vector2D(config.WINDOW_WIDTH - 150, 115)
        radius = size * 0.8 * (1 + 0.12 * math.sin(self.time * 2.4))
        shadow_center = o_center + Vector2D(4, 5)
        draw_ring_arc(surface, darken(config.COLOR_O), o_arc_points(shadow_center, radius), shadow_center, 12)
        draw_ring_arc(surface, config.COLOR_O, o_arc_points(o_center, radius), o_center, 12)
