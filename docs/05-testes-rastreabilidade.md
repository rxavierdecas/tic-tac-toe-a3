# 5. Plano de Testes e Matriz de Rastreabilidade

## 5.1 Plano de testes

| Item | Descrição |
|---|---|
| Objetivo | Verificar regras, alternância de turnos, jogadas proibidas, pontuação, colisão (hit-test do mouse com as células) e efeitos gráficos. |
| Tipos | **Unitários automatizados** (pytest, 86 casos em `tests/`) e **testes de sistema manuais** (partida completa na tela). |
| Ambiente | Python 3.10+, Pygame 2.5+, Windows/Linux/macOS. Os testes de widgets usam `SDL_VIDEODRIVER=dummy`, sem janela. |
| Execução | `python -m pytest` na raiz do projeto. |
| Critério de aceite | 100% dos testes automatizados passando e todos os casos manuais com o resultado esperado. |

**Testes automatizados por módulo**

| Arquivo | Escopo |
|---|---|
| `test_board.py` | 8 linhas vencedoras, vitória (linha, coluna, diagonais), velha, casa ocupada, fora do tabuleiro |
| `test_game_engine.py` | alternância de turnos, jogadas inválidas, placar, velhas, pausa, cronômetro, revanche, reinício |
| `test_player.py` | placar e nome padrão |
| `test_coords.py` | conversão mundo ↔ tela e hit-test (colisão ponto-célula) |
| `test_vector2d.py`, `test_transform.py` | álgebra vetorial e matrizes de translação, rotação, escala, composição e inversa |
| `test_shapes.py` | geometria do X e do O e traçado parcial |
| `test_animation.py` | tweens e easing |
| `test_particles.py`, `test_effects.py` | física das partículas, linha vencedora e tremor |
| `test_widgets.py`, `test_game_scene.py` | botão, campo de texto, mapeamento das teclas 1–9 e cronômetro |

## 5.2 Casos de teste detalhados

| ID | Caso | Entrada | Procedimento | Resultado esperado | Resultado obtido | Teste automatizado |
|---|---|---|---|---|---|---|
| CT01 | Alternância de turnos | Jogadas (0,0) e depois (1,1) | Iniciar uma partida e fazer duas jogadas válidas | X começa; após a 1ª jogada a vez é de O; após a 2ª volta para X | ✅ Conforme esperado | `test_game_engine::test_x_comeca_e_turnos_alternam` |
| CT02 | Jogada em casa ocupada (movimento proibido) | X joga (0,0); O tenta (0,0) | Tentar marcar uma casa já ocupada | Retorna `INVALID_OCCUPIED`, a casa continua com X e a vez continua com O. Na tela, a casa treme e pisca em vermelho. | ✅ Conforme esperado | `test_game_engine::test_jogada_invalida_nao_troca_turno`, `test_board::test_jogada_em_casa_ocupada_e_rejeitada` |
| CT03 | Vitória e pontuação | X: (0,0),(0,1),(0,2); O: (1,0),(1,1) | Jogar alternadamente até X completar a linha 0 | Estado `WIN`, vencedor X, linha ((0,0),(0,1),(0,2)), placar X = 1 e O = 0. Na tela aparecem a linha brilhante, as partículas e o painel "Vitória de ...". | ✅ Conforme esperado | `test_game_engine::test_vitoria_atualiza_estado_e_placar` |
| CT04 | Vitória em todas as direções | Tabuleiros com linha, coluna, diagonal principal e diagonal secundária completas | Chamar `Board.winner()` | Retorna o símbolo e a linha vencedora correta | ✅ Conforme esperado | `test_board::test_vitoria_em_linha_coluna_e_diagonais` |
| CT05 | Empate (velha) | Sequência X O X / X O O / O X X | Preencher as 9 casas sem formar linha | Estado `DRAW`, velhas = 1, sem vencedor. Na tela aparece o painel "Deu velha!". | ✅ Conforme esperado | `test_game_engine::test_velha_incrementa_empates`, `test_board::test_velha` |
| CT06 | Jogada após o fim de jogo | Partida encerrada com vitória de X; tentativa de jogar em (2,2) | Tentar jogar após a vitória | Retorna `GAME_OVER` e a casa (2,2) continua vazia | ✅ Conforme esperado | `test_game_engine::test_jogada_apos_fim_de_jogo_e_rejeitada` |
| CT07 | Pausa | `toggle_pause()`; jogada em (0,0); `tick(5 s)` | Pausar, tentar jogar e avançar o tempo | Jogada rejeitada (`PAUSED`) e cronômetro inalterado. Depois de despausar, a jogada é aceita. | ✅ Conforme esperado | `test_game_engine::test_pausa_bloqueia_jogadas_e_cronometro` |
| CT08 | Colisão do clique com as células (hit-test) | Tabuleiro de 300 px em (100,50); cliques em (250,200), (399,349) e (99,60) | Converter a posição de tela em célula por `M⁻¹` | (1,1); (2,2); `None` (fora do tabuleiro) | ✅ Conforme esperado | `test_coords::test_hit_test_do_mouse`, `test_coords::test_clique_fora_do_tabuleiro` |
| CT09 | Revanche | Fim de partida e acionamento de `rematch()` | Pedir revanche | Tabuleiro vazio, O começa, placar mantido, partida nº 2 | ✅ Conforme esperado | `test_game_engine::test_revanche_alterna_quem_comeca_e_mantem_placar` |
| CT10 | Reinício | Uma jogada feita e depois `restart()` | Reiniciar a partida | Tabuleiro vazio, X começa e o número da partida não muda | ✅ Conforme esperado | `test_game_engine::test_restart_mantem_jogador_inicial` |
| CT11 | Transformações matriciais | Ponto (1,0) com `T(100,50)·R(90°)·S(2)` | Aplicar a matriz composta | (100, 52): escala, depois rotação, depois translação | ✅ Conforme esperado | `test_transform::test_composicao_trs_aplica_escala_rotacao_translacao_nessa_ordem` |
| CT12 | Geometria do X e do O | Centro (100,100); X com meia-diagonal 10√2; O com raio 20 e 32 segmentos | Gerar os traços e os pontos | X com traços de (90,90) a (110,110) e de (110,90) a (90,110); O fechado, com todos os pontos à distância 20 do centro | ✅ Conforme esperado | `test_shapes::test_x_formado_por_dois_tracos_diagonais_simetricos`, `test_shapes::test_o_completo_fecha_o_circulo_e_mantem_raio` |
| CT13 | Partículas da vitória | `WinLineEffect` na linha 0 e `update(2 s)` | Avançar o efeito até o fechamento | `closed = True` e as partículas são emitidas uma única vez | ✅ Conforme esperado | `test_effects::test_fechamento_da_linha_dispara_particulas_uma_vez` |
| CT14 | Teclado numérico | Teclas 7, 5 e 3 | Converter a tecla em célula | (0,0), (1,1) e (2,2) | ✅ Conforme esperado | `test_game_scene::test_teclas_seguem_layout_do_teclado_numerico` |
| CT15 | Nomes dos jogadores | Nome "   " e entrada de "Joãozinho" com limite de 5 caracteres | Criar o jogador e digitar no campo | Nome padrão "Jogador O"; o texto fica truncado em "Joãoz" | ✅ Conforme esperado | `test_player::test_nome_vazio_recebe_padrao`, `test_widgets::test_text_input_foco_digitacao_e_limite` |
| CT16 | Desempenho (sistema, manual) | Partida completa com efeitos ativos | Rodar `python main.py`, pressionar F3 e jogar até a vitória | O contador mostra ≈ 60 FPS estáveis | A preencher pelo grupo na máquina da banca | — |
| CT17 | Fluxo completo (sistema, manual) | Menu → partida → vitória → revanche → velha → menu | Jogar com 2 pessoas | Todas as telas aparecem e o placar é acumulado corretamente | A preencher pelo grupo | — |

## 5.3 Matriz de Rastreabilidade (RF ↔ Caso de Uso ↔ Caso de Teste)

| Requisito | Descrição resumida | Caso(s) de Uso | Caso(s) de Teste |
|---|---|---|---|
| RF01 | Identificar os jogadores | UC01 | CT15, CT17 |
| RF02 | Alternar turnos | UC02 | CT01, CT09, CT10 |
| RF03 | Jogada por mouse e teclado | UC02 | CT08, CT14 |
| RF04 | Rejeitar jogadas inválidas | UC02 | CT02, CT06, CT07, CT08 |
| RF05 | Detectar vitória | UC02, UC05 | CT03, CT04 |
| RF06 | Detectar velha | UC02, UC05 | CT05 |
| RF07 | Placar entre partidas | UC05, UC06 | CT03, CT05, CT09 |
| RF08 | Pausar e retomar | UC03 | CT07 |
| RF09 | Reiniciar partida | UC04 | CT10 |
| RF10 | Tela de fim de jogo, revanche e menu | UC05, UC06, UC07 | CT09, CT17 |
| RF11 | HUD (placar, vez, cronômetro) | UC02, UC03 | CT07, CT17 |
| RF12 | Traçado animado e efeito da linha vencedora | UC02, UC05 | CT11, CT12, CT13 |
| RNF01 | 60 FPS | — | CT16 |
