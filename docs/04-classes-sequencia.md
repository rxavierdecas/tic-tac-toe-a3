# 4. Modelagem Estrutural e Dinâmica

> Os diagramas estão em **PlantUML**. Para gerar as imagens, use a extensão *PlantUML* do VS Code ou <https://www.plantuml.com/plantuml>.

## 4.1 Diagrama de Classes

A arquitetura tem três camadas:

- **core**: matemática de computação gráfica.
- **model**: regras do jogo, sem dependência do Pygame.
- **graphics/ui**: apresentação.

As dependências apontam sempre da apresentação para o modelo.

```plantuml
@startuml classes
skinparam classAttributeIconSize 0
hide empty members

package core {
  class Vector2D <<dataclass>> {
    + x : float
    + y : float
    + __add__(o : Vector2D) : Vector2D
    + __sub__(o : Vector2D) : Vector2D
    + __mul__(k : float) : Vector2D
    + dot(o : Vector2D) : float
    + length() : float
    + normalized() : Vector2D
    + lerp(target : Vector2D, t : float) : Vector2D
    + {static} from_angle(a : float, len : float) : Vector2D
  }
  class Matrix3 {
    - _m : float[3][3]
    + {static} identity() : Matrix3
    + {static} translation(tx, ty) : Matrix3
    + {static} rotation(angle) : Matrix3
    + {static} scale(sx, sy) : Matrix3
    + {static} trs(pos, angle, scale) : Matrix3
    + __matmul__(o : Matrix3) : Matrix3
    + apply(p : Vector2D) : Vector2D
    + apply_vector(v : Vector2D) : Vector2D
    + inverse() : Matrix3
  }
  Matrix3 ..> Vector2D
}

package model {
  class Player {
    + name : str
    + symbol : str
    + color : RGB
    + score : int
    + add_win() : void
    + reset_score() : void
  }
  class Board {
    + cells : str[3][3]
    + {static} WIN_LINES : Line[8]
    + is_valid_move(r, c) : bool
    + place(r, c, symbol) : bool
    + winner() : (str, Line)
    + is_full() : bool
    + is_draw() : bool
    + reset() : void
  }
  enum GameState {
    PLAYING
    PAUSED
    WIN
    DRAW
  }
  enum MoveResult {
    OK
    WIN
    DRAW
    INVALID_OCCUPIED
    INVALID_OUT_OF_BOUNDS
    GAME_OVER
    PAUSED
  }
  class GameEngine {
    + state : GameState
    + winner : Player
    + winning_line : Line
    + draws : int
    + round : int
    + elapsed : float
    + current_player : Player
    + play(r, c) : MoveResult
    + toggle_pause() : bool
    + restart() : void
    + rematch() : void
    + tick(dt) : void
    - _check_end() : MoveResult
    - _switch_turn() : void
  }
  GameEngine "1" *-- "1" Board
  GameEngine "1" o-- "2" Player : players
  GameEngine --> GameState
  GameEngine ..> MoveResult
}

package graphics {
  class BoardLayout {
    + world_to_screen : Matrix3
    + screen_to_world : Matrix3
    + cell_size : float
    + cell_from_screen(pos) : (int, int)
    + cell_center(r, c) : Vector2D
    + grid_lines() : Segment[4]
  }
  class Tween {
    + duration : float
    + delay : float
    + value : float
    + finished : bool
    + update(dt) : void
  }
  class GridRenderer {
    + update(dt) : void
    + draw(surface) : void
  }
  class AnimatedSymbol {
    + symbol : str
    + row : int
    + col : int
    + highlight : float
    + update(dt) : void
    + draw(surface, layout, offset) : void
  }
  class Particle {
    + position : Vector2D
    + velocity : Vector2D
    + life : float
    + update(dt, gravity, drag) : void
  }
  class ParticleSystem {
    + emit(pos, n, color) : void
    + emit_along(p0, p1, n, color) : void
    + update(dt) : void
    + draw(surface) : void
  }
  class WinLineEffect {
    + start : Vector2D
    + end : Vector2D
    + closed : bool
    + pulse : float
    + update(dt) : void
    + draw(surface) : void
  }
  class ShakeEffect {
    + offset : Vector2D
    + trigger(cell) : void
    + update(dt) : void
  }
  BoardLayout --> Matrix3
  GridRenderer --> BoardLayout
  GridRenderer "1" *-- "4" Tween
  AnimatedSymbol "1" *-- "2" Tween
  ParticleSystem "1" *-- "0..*" Particle
  WinLineEffect --> ParticleSystem
  WinLineEffect *-- Tween
}

package ui {
  abstract class Scene {
    # app : App
    + on_enter() : void
    + handle_event(e) : void
    + update(dt) : void
    + draw(surface) : void
  }
  class MenuScene {
    + start_game() : void
  }
  class GameScene {
    + try_move(r, c) : MoveResult
    + rematch() : void
    + restart_round() : void
    + go_to_menu() : void
  }
  class GameOverPanel {
    + handle_event(e) : str
    + update(dt) : void
    + draw(surface) : void
  }
  class Button
  class TextInput
  class App {
    + scene : Scene
    + clock : Clock
    + run(initial) : void
    + change_scene(s : Scene) : void
  }
  Scene <|-- MenuScene
  Scene <|-- GameScene
  App "1" o-- "1" Scene
  MenuScene "1" *-- "2" TextInput
  MenuScene "1" *-- "2" Button
  GameOverPanel "1" *-- "2" Button
  GameScene --> GameEngine
  GameScene "1" *-- "1" BoardLayout
  GameScene "1" *-- "1" GridRenderer
  GameScene "1" *-- "0..9" AnimatedSymbol
  GameScene "1" *-- "1" ParticleSystem
  GameScene "1" *-- "0..1" WinLineEffect
  GameScene "1" *-- "1" ShakeEffect
  GameScene "1" *-- "0..1" GameOverPanel
  MenuScene ..> GameEngine : cria
}
@enduml
```

## 4.2 Diagrama de Sequência 1 — Processamento e validação de uma jogada

```plantuml
@startuml seq-jogada
actor "Jogador da vez" as J
participant App
participant GameScene as GS
participant BoardLayout as BL
participant GameEngine as GE
participant Board as B
participant AnimatedSymbol as AS
participant ParticleSystem as PS
participant ShakeEffect as SH

J -> App : clique (x, y)
App -> GS : handle_event(MOUSEBUTTONDOWN)
GS -> BL : cell_from_screen((x, y))
BL -> BL : mundo = M⁻¹ · (x, y, 1)
BL --> GS : (linha, coluna) | None
alt clique fora do tabuleiro
  GS --> J : ignora
else célula válida
  GS -> GE : play(linha, coluna)
  alt state == PAUSED
    GE --> GS : MoveResult.PAUSED
  else partida encerrada
    GE --> GS : MoveResult.GAME_OVER
  else em andamento
    GE -> B : place(linha, coluna, símbolo)
    alt casa ocupada
      B --> GE : False
      GE --> GS : MoveResult.INVALID_OCCUPIED
      GS -> SH : trigger(célula)
      note right of SH : tremor + flash vermelho;\nturno NÃO muda
    else casa vazia
      B --> GE : True
      GE -> GE : _check_end()
      GE -> GE : _switch_turn()
      GE --> GS : MoveResult.OK
      GS -> AS ** : new(símbolo, linha, coluna, cor)
      GS -> PS : emit(centro, 14, cor)
    end
  end
end
loop a cada quadro (60 FPS)
  App -> GS : update(dt)
  GS -> AS : update(dt)  (traçado P(t) = P0 + (P1 − P0)·t)
  App -> GS : draw(tela)
end
@enduml
```

## 4.3 Diagrama de Sequência 2 — Verificação de fim de jogo e animação de vitória

```plantuml
@startuml seq-vitoria
participant GameScene as GS
participant GameEngine as GE
participant Board as B
participant Player as P
participant WinLineEffect as WL
participant ParticleSystem as PS
participant GameOverPanel as GO

GS -> GE : play(linha, coluna)
GE -> B : place(...)
GE -> GE : _check_end()
GE -> B : winner()
loop para cada uma das 8 WIN_LINES
  B -> B : compara as 3 células
end
alt linha completa
  B --> GE : (símbolo, linha)
  GE -> GE : state = WIN; winner; winning_line
  GE -> P : add_win()
  GE --> GS : MoveResult.WIN
  GS -> WL ** : new(layout, linha, cor, particles)
else tabuleiro cheio
  B --> GE : None
  GE -> B : is_full()
  GE -> GE : state = DRAW; draws += 1
  GE --> GS : MoveResult.DRAW
  GS -> PS : emit(centro de cada célula, cor âmbar)
end

loop a cada quadro, após o traçado do último símbolo
  GS -> WL : update(dt)
  WL -> WL : trace.update(dt) — linha cresce de start até end
  opt trace terminou (primeira vez)
    WL -> PS : emit_along(start, end, 90)
    WL -> PS : emit(pontas, 40)
    WL -> WL : closed = True; inicia onda de choque
  end
  GS -> GS : highlight dos símbolos = pulse (seno)
  GS -> GS : end_timer += dt
end

opt end_timer ≥ 1,2 s e onda de choque concluída
  GS -> GO ** : new(engine)
  GO -> GO : animação de escala (ease_out_back) e fade
end
@enduml
```
