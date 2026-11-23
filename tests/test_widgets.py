import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402
import pytest  # noqa: E402

from tictactoe.ui.widgets import Button, TextInput  # noqa: E402


@pytest.fixture(autouse=True, scope="module")
def pygame_init():
    pygame.init()
    yield
    pygame.quit()


def click(pos):
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pos)


def test_botao_detecta_clique_dentro_e_ignora_fora():
    b = Button((100, 100), (80, 40), "OK")
    assert b.handle_event(click((100, 100)))
    assert not b.handle_event(click((10, 10)))


def test_botao_hover_suavizado():
    b = Button((100, 100), (80, 40), "OK")
    b.handle_event(pygame.event.Event(pygame.MOUSEMOTION, pos=(100, 100)))
    b.update(1.0)
    assert b.hover == pytest.approx(1.0)


def test_text_input_foco_digitacao_e_limite():
    t = TextInput((0, 0, 200, 40), max_length=5)
    t.handle_event(pygame.event.Event(pygame.TEXTINPUT, text="abc"))
    assert t.text == ""  # sem foco, ignora
    t.handle_event(click((10, 10)))
    assert t.focused
    t.handle_event(pygame.event.Event(pygame.TEXTINPUT, text="Joãozinho"))
    assert t.text == "Joãoz"
    t.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_BACKSPACE))
    assert t.text == "João"
    assert t.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
