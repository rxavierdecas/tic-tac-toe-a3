# Jogo da Velha — A3 Computação Gráfica (Grupo 01)

Jogo da Velha clássico (3x3) para **2 jogadores locais**, desenvolvido em **Python + Pygame** como
trabalho de conclusão da UC *Computação Gráfica e Realidade Virtual* (Ciência da Computação, 2026/2).

Todo o desenho é **geométrico/vetorial**: grade, X, O e linha vencedora são gerados por vetores e
matrizes de transformação, com animação de traçado, sombras, brilho e sistema de partículas.

## Requisitos

- Python **3.10+** (Windows, Linux ou macOS)
- Pygame 2.5+ (instalado via `requirements.txt`)

## Instalação

```bash
python -m venv .venv
# Windows:      .venv\Scripts\activate
# Linux/macOS:  source .venv/bin/activate
pip install -r requirements.txt
```

## Execução

```bash
python main.py
```

## Como jogar

1. No **menu**, digite o nome do Jogador 1 (X) e do Jogador 2 (O) — `Tab` alterna o campo — e clique em **Jogar** (ou `Enter`).
2. Os jogadores se alternam no mesmo computador. O jogador da vez é indicado pelo cartão iluminado e pelo texto "Vez de ...".
3. Vence quem completar uma linha, coluna ou diagonal. Tabuleiro cheio sem vencedor = **velha**.
4. Na tela de fim de jogo escolha **Revanche** (quem começa alterna e o placar é mantido) ou **Menu**.

### Controles

| Ação | Tecla / Mouse |
|---|---|
| Marcar casa | Clique esquerdo **ou** teclas `1`–`9` (layout do teclado numérico: `7 8 9` no topo, `1 2 3` embaixo) |
| Pausar / continuar | `P` (ou `ESC` durante a partida) |
| Voltar ao menu | `ESC` com o jogo pausado ou no fim de jogo |
| Reiniciar partida atual | `R` |
| Revanche (fim de jogo) | `Enter`, `R`, `Espaço` ou botão **Revanche** |
| Mostrar FPS | `F3` |

Jogadas inválidas (casa ocupada, jogo pausado ou encerrado) são rejeitadas; a casa ocupada pisca em vermelho e treme.

## Testes

```bash
python -m pytest
```

Os testes cobrem vetores, matrizes, regras do tabuleiro, motor de jogo (turnos, pausa, placar,
revanche), mapeamento de coordenadas, animações, partículas, efeitos e widgets.

## Arquitetura

```
main.py                     ponto de entrada
src/tictactoe/
├── config.py               janela, 60 FPS, layout, paleta e durações
├── app.py                  App: laço principal (eventos → update(dt) → draw) e troca de cenas
├── core/
│   ├── vector2d.py         Vector2D: soma, escalar, produto escalar, norma, lerp
│   └── transform.py        Matrix3: translação, rotação, escala, composição e inversa
├── model/                  regras puras (sem Pygame)
│   ├── player.py           Player: nome, símbolo, cor, placar
│   ├── board.py            Board: matriz 3x3, 8 linhas vencedoras, vitória/velha
│   └── game_engine.py      GameEngine: turnos, estados, pausa, revanche, cronômetro
├── graphics/
│   ├── coords.py           BoardLayout: mundo (células) ↔ tela (pixels) via matrizes
│   ├── animation.py        Tween e funções de easing
│   ├── shapes.py           GridRenderer e AnimatedSymbol (X/O com traçado animado)
│   ├── particles.py        Particle e ParticleSystem
│   └── effects.py          WinLineEffect (linha vencedora) e ShakeEffect
└── ui/
    ├── widgets.py          Button, TextInput, desenho de texto
    └── scenes/             MenuScene, GameScene, GameOverPanel
tests/                      testes automatizados (pytest)
docs/                       requisitos, telas, UML, plano de testes e rastreabilidade
```

A camada `model` não depende da camada gráfica: as regras podem ser testadas isoladamente e a
`GameScene` apenas traduz os resultados do `GameEngine` (`MoveResult`) em feedback visual.

## Conceitos de Computação Gráfica aplicados

| Conceito | Onde |
|---|---|
| Sistemas de coordenadas mundo ↔ tela | `BoardLayout`: `M = T(origem)·S(célula)` e a inversa `M⁻¹` no clique do mouse |
| Matrizes homogêneas 3x3 (translação, rotação, escala) | `Matrix3`; o X é um segmento-base transformado por `T·R(45°)·S`; o logo do menu gira com `R(θ(t))` |
| Vetores | `Vector2D` em posições, velocidades, direções da linha vencedora e normais do anel do O |
| Geração de primitivas/polígonos | O é um polígono gerado pela rotação incremental do vetor raio; arco grosso como polígono em anel |
| Animação de traçado | Interpolação linear `P(t) = P0 + (P1 − P0)·t` com easing para grade, X, O e linha vencedora |
| Efeito de vitória | Linha com camadas de brilho (glow) pulsante, onda de choque com escala crescente e partículas |
| Sistema de partículas | Integração de Euler com gravidade, arrasto e fade por alpha |
| Iluminação/sombras básicas | Sombra deslocada dos símbolos, botões e painéis; destaque luminoso das células vencedoras |
| Controle de framerate | `clock.tick(60)` e animações baseadas em `dt` (independentes do FPS) |

## Documentação

Veja a pasta [`docs/`](docs/) para requisitos, wireframes, casos de uso, diagramas UML (PlantUML),
plano de testes e matriz de rastreabilidade.
