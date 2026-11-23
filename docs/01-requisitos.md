# 1. Visão Geral e Levantamento de Requisitos

## 1.1 Declaração de escopo

**Produto:** Jogo da Velha (Tic-Tac-Toe) clássico 3x3 para 2 jogadores locais, em Python com Pygame.

**Regras do jogo**

- O tabuleiro é uma matriz 3x3 inicialmente vazia.
- O Jogador 1 usa **X** e o Jogador 2 usa **O**. Na primeira partida, X começa; nas revanches, quem começa se alterna.
- Os jogadores se revezam marcando uma casa vazia por turno.
- Vence quem completar primeiro uma das **8 linhas**: 3 horizontais, 3 verticais ou 2 diagonais.
- Se as 9 casas forem preenchidas sem vencedor, a partida termina **empatada (velha)**.
- Não é permitido marcar casa ocupada, jogar com a partida pausada ou após o fim da partida.

**Fora do escopo:** modo contra computador, partidas em rede e a variante Ultimate Tic-Tac-Toe.

## 1.2 Público-alvo

- Jogadores casuais de qualquer idade que dividem o mesmo computador.
- Estudantes e professores de Computação Gráfica interessados em ver conceitos de transformações, animação e partículas aplicados a um jogo simples.

## 1.3 Objetivos didáticos

- Aplicar **sistemas de coordenadas** (mundo ↔ tela) e **matrizes homogêneas** de translação, rotação e escala.
- Construir primitivas e polígonos de forma procedural (X por segmentos transformados, O por rotação incremental de vetor).
- Implementar **animações** temporizadas por `dt`, um **sistema de partículas** e efeitos de brilho e sombra.
- Exercitar engenharia de software: arquitetura em camadas, UML, testes automatizados e rastreabilidade.

## 1.4 Requisitos Funcionais (RF)

| ID | Requisito | Prioridade |
|---|---|---|
| RF01 | Permitir identificar os dois jogadores (nomes) no menu inicial; nomes vazios recebem um padrão. | Alta |
| RF02 | Alternar o turno entre X e O após cada jogada válida, indicando claramente na interface quem joga. | Alta |
| RF03 | Permitir a jogada por clique do mouse na casa ou pelas teclas 1–9 (layout do teclado numérico). | Alta |
| RF04 | Rejeitar jogadas inválidas (casa ocupada, fora do tabuleiro, jogo pausado ou encerrado) sem trocar o turno, com feedback visual. | Alta |
| RF05 | Detectar vitória em qualquer uma das 8 linhas e identificar a linha vencedora. | Alta |
| RF06 | Detectar empate (velha) quando o tabuleiro estiver cheio sem vencedor. | Alta |
| RF07 | Manter o placar de vitórias de cada jogador e o número de velhas entre partidas. | Média |
| RF08 | Pausar e retomar a partida; durante a pausa o cronômetro e as jogadas ficam bloqueados. | Média |
| RF09 | Reiniciar a partida atual mantendo o placar. | Média |
| RF10 | Exibir tela de fim de jogo (vitória ou velha) com opções de revanche (alternando quem começa) e de retorno ao menu. | Alta |
| RF11 | Exibir HUD com nomes, placar, indicador de vez, número da partida, velhas e cronômetro. | Alta |
| RF12 | Desenhar grade, X e O com animação de traçado e destacar a linha vencedora com efeitos visuais (brilho e partículas). | Alta |

## 1.5 Requisitos Não Funcionais (RNF)

| ID | Categoria | Requisito |
|---|---|---|
| RNF01 | Desempenho | Taxa de quadros travada em **60 FPS** (`clock.tick(60)`), com animações baseadas em `dt`. |
| RNF02 | Portabilidade | Executar em **Python 3.10+** em Windows, Linux e macOS, usando apenas Pygame e a fonte padrão. |
| RNF03 | Responsividade | Entrada processada no mesmo quadro em que ocorre (latência ≤ 1 quadro ≈ 16,7 ms). |
| RNF04 | Estética e ergonomia | Cores de alto contraste e distintas por jogador (X vermelho/rosa, O ciano) e textos legíveis. |
| RNF05 | Manutenibilidade | Regras isoladas da camada gráfica (`model/`), cobertas por testes automatizados (pytest). |
| RNF06 | Usabilidade | Instruções de controle visíveis no menu e durante a partida. |
| RNF07 | Robustez | Dados de entrada inválidos (cliques fora do tabuleiro, teclas não mapeadas) são ignorados sem erro. |
