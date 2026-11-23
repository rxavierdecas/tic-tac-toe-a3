"""Constantes globais: janela, framerate, layout e paleta de cores."""

# Janela
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Jogo da Velha — Grupo 01"
FPS = 60

# Layout do tabuleiro (coordenadas de tela, em pixels)
BOARD_SIZE = 480                      # lado do tabuleiro
BOARD_ORIGIN = ((WINDOW_WIDTH - BOARD_SIZE) // 2, 170)  # canto superior esquerdo
GRID_LINE_WIDTH = 8
SYMBOL_LINE_WIDTH = 14
SYMBOL_PADDING = 0.22                 # margem do símbolo, em fração da célula

# Durações de animação (segundos)
GRID_DRAW_TIME = 0.6
SYMBOL_DRAW_TIME = 0.35
WIN_LINE_DRAW_TIME = 0.5
GAME_OVER_DELAY = 1.2
SHAKE_TIME = 0.3

# Paleta (RGB)
COLOR_BG = (18, 20, 33)
COLOR_BG_ACCENT = (28, 31, 51)
COLOR_GRID = (90, 98, 140)
COLOR_TEXT = (235, 238, 250)
COLOR_TEXT_DIM = (140, 146, 180)
COLOR_X = (255, 90, 110)              # Jogador 1 — vermelho/rosa
COLOR_O = (70, 200, 255)              # Jogador 2 — ciano
COLOR_DRAW = (250, 205, 90)
COLOR_INVALID = (255, 60, 60)
COLOR_BUTTON = (50, 56, 92)
COLOR_BUTTON_HOVER = (80, 90, 145)
COLOR_OVERLAY = (0, 0, 0, 170)

# Fontes (None = fonte padrão do Pygame, garante portabilidade)
FONT_NAME = None
FONT_SIZE_TITLE = 72
FONT_SIZE_LARGE = 48
FONT_SIZE_MEDIUM = 32
FONT_SIZE_SMALL = 24
