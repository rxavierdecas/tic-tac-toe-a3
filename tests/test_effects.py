import random

import pytest

from tictactoe.core.vector2d import Vector2D
from tictactoe.graphics.coords import BoardLayout
from tictactoe.graphics.effects import ShakeEffect, WinLineEffect
from tictactoe.graphics.particles import ParticleSystem


def make_effect():
    layout = BoardLayout((0, 0), 300)
    ps = ParticleSystem(random.Random(0))
    effect = WinLineEffect(layout, ((0, 0), (0, 1), (0, 2)), (255, 0, 0), ps)
    return effect, ps


def test_linha_vencedora_estende_alem_dos_centros():
    effect, _ = make_effect()
    assert effect.start.x < 50 and effect.end.x > 250
    assert effect.start.y == pytest.approx(50)
    assert effect.midpoint == Vector2D(150, 50)


def test_fechamento_da_linha_dispara_particulas_uma_vez():
    effect, ps = make_effect()
    effect.update(0.1)
    assert not effect.closed
    assert len(ps) == 0
    effect.update(2.0)
    assert effect.closed
    count = len(ps)
    assert count > 0
    effect.update(0.01)
    assert len(ps) <= count  # não emite de novo


def test_shake_inativo_por_padrao_e_amortece():
    shake = ShakeEffect(duration=0.3)
    assert not shake.active
    assert shake.offset == Vector2D()
    shake.trigger((1, 1))
    assert shake.active and shake.cell == (1, 1)
    shake.update(0.01)
    assert abs(shake.offset.x) > 0
    shake.update(1.0)
    assert not shake.active
    assert shake.offset == Vector2D()
