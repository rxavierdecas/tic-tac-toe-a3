"""Componentes de interface: fontes, texto, botão e campo de texto."""

from __future__ import annotations

from functools import lru_cache

import pygame

from tictactoe import config


@lru_cache(maxsize=None)
def get_font(size: int) -> pygame.font.Font:
    """Fonte padrão em cache (evita recriar a cada quadro)."""
    return pygame.font.Font(config.FONT_NAME, size)


def draw_text(surface, text: str, size: int, color, center=None, topleft=None, midleft=None,
              midright=None) -> pygame.Rect:
    """Renderiza texto anti-aliased e o posiciona pela âncora informada."""
    image = get_font(size).render(text, True, color)
    rect = image.get_rect()
    if center is not None:
        rect.center = center
    elif topleft is not None:
        rect.topleft = topleft
    elif midleft is not None:
        rect.midleft = midleft
    elif midright is not None:
        rect.midright = midright
    surface.blit(image, rect)
    return rect


class Button:
    """Botão com realce de hover (cor e escala interpoladas) e clique."""

    def __init__(self, center: tuple[int, int], size: tuple[int, int], label: str,
                 font_size: int = config.FONT_SIZE_MEDIUM, accent=None) -> None:
        self.center = center
        self.size = size
        self.label = label
        self.font_size = font_size
        self.accent = accent or config.COLOR_BUTTON_HOVER
        self.hover = 0.0          # 0..1, suavizado ao longo do tempo
        self._hovered = False

    @property
    def rect(self) -> pygame.Rect:
        r = pygame.Rect(0, 0, *self.size)
        r.center = self.center
        return r

    def handle_event(self, event) -> bool:
        """Retorna True quando o botão é clicado com o botão esquerdo."""
        if event.type == pygame.MOUSEMOTION:
            self._hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False

    def update(self, dt: float) -> None:
        target = 1.0 if self._hovered else 0.0
        self.hover += (target - self.hover) * min(1.0, dt * 12)

    def draw(self, surface) -> None:
        scale = 1.0 + 0.06 * self.hover
        w, h = self.size
        rect = pygame.Rect(0, 0, round(w * scale), round(h * scale))
        rect.center = self.center
        base, accent = config.COLOR_BUTTON, self.accent
        color = tuple(round(b + (a - b) * self.hover) for b, a in zip(base, accent))
        shadow = rect.move(0, 5)
        pygame.draw.rect(surface, (8, 9, 16), shadow, border_radius=14)
        pygame.draw.rect(surface, color, rect, border_radius=14)
        pygame.draw.rect(surface, accent, rect, width=2, border_radius=14)
        draw_text(surface, self.label, self.font_size, config.COLOR_TEXT, center=rect.center)


class TextInput:
    """Campo de texto de uma linha para o nome do jogador."""

    def __init__(self, rect: tuple[int, int, int, int], text: str = "", max_length: int = 14,
                 accent=(255, 255, 255), placeholder: str = "") -> None:
        self.rect = pygame.Rect(rect)
        self.text = text
        self.max_length = max_length
        self.accent = accent
        self.placeholder = placeholder
        self.focused = False
        self._blink = 0.0

    def handle_event(self, event) -> bool:
        """Processa foco e digitação. Retorna True se Enter foi pressionado."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.focused = self.rect.collidepoint(event.pos)
        elif self.focused and event.type == pygame.TEXTINPUT:
            if len(self.text) < self.max_length and event.text.isprintable():
                self.text += event.text
                self.text = self.text[: self.max_length]
        elif self.focused and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return True
        return False

    def update(self, dt: float) -> None:
        self._blink = (self._blink + dt) % 1.0

    def draw(self, surface) -> None:
        border = self.accent if self.focused else config.COLOR_GRID
        pygame.draw.rect(surface, config.COLOR_BG_ACCENT, self.rect, border_radius=10)
        pygame.draw.rect(surface, border, self.rect, width=3, border_radius=10)
        x = self.rect.x + 14
        if self.text:
            text_rect = draw_text(surface, self.text, config.FONT_SIZE_MEDIUM, config.COLOR_TEXT,
                                  midleft=(x, self.rect.centery))
            x = text_rect.right + 2
        elif not self.focused:
            draw_text(surface, self.placeholder, config.FONT_SIZE_MEDIUM, config.COLOR_TEXT_DIM,
                      midleft=(x, self.rect.centery))
        if self.focused and self._blink < 0.5:
            top = self.rect.centery - 12
            pygame.draw.line(surface, self.accent, (x, top), (x, top + 24), 2)
