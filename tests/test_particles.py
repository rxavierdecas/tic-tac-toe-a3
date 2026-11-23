import random

import pytest

from tictactoe.core.vector2d import Vector2D
from tictactoe.graphics.particles import Particle, ParticleSystem


def test_particula_sofre_gravidade_e_se_move():
    p = Particle(Vector2D(0, 0), Vector2D(100, 0), life=1.0, color=(255, 0, 0))
    p.update(0.1, gravity=Vector2D(0, 100), drag=1.0)
    assert p.velocity == Vector2D(100, 10)
    assert p.position.x == pytest.approx(10)
    assert p.position.y == pytest.approx(1)


def test_vida_e_razao_decaem():
    p = Particle(Vector2D(), Vector2D(), life=1.0, color=(0, 0, 0))
    p.update(0.25)
    assert p.ratio == pytest.approx(0.75)
    p.update(1.0)
    assert not p.alive
    assert p.ratio == 0.0


def test_emit_cria_quantidade_pedida():
    ps = ParticleSystem(random.Random(42))
    ps.emit(Vector2D(10, 10), 30, (255, 255, 255))
    assert len(ps) == 30


def test_emit_along_distribui_no_segmento():
    ps = ParticleSystem(random.Random(1))
    ps.emit_along(Vector2D(0, 0), Vector2D(100, 0), 5, (1, 2, 3))
    xs = sorted(p.position.x for p in ps.particles)
    assert xs == [0, 25, 50, 75, 100]


def test_particulas_mortas_sao_removidas():
    ps = ParticleSystem(random.Random(0))
    ps.emit(Vector2D(), 50, (255, 0, 0), life=(0.2, 0.4))
    ps.update(0.5)
    assert len(ps) == 0


def test_limite_maximo_de_particulas():
    ps = ParticleSystem(random.Random(0), max_particles=10)
    ps.emit(Vector2D(), 100, (0, 0, 0))
    assert len(ps) == 10
