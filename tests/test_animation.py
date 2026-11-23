import pytest

from tictactoe.graphics.animation import (
    Tween,
    ease_in_out_sine,
    ease_out_back,
    ease_out_cubic,
    linear,
)


@pytest.mark.parametrize("fn", [linear, ease_out_cubic, ease_in_out_sine, ease_out_back])
def test_easing_comeca_em_0_e_termina_em_1(fn):
    assert fn(0.0) == pytest.approx(0.0, abs=1e-9)
    assert fn(1.0) == pytest.approx(1.0)


def test_ease_out_back_ultrapassa_destino():
    assert max(ease_out_back(t / 100) for t in range(101)) > 1.0


def test_tween_progride_com_dt_e_termina():
    tw = Tween(1.0, linear)
    tw.update(0.25)
    assert tw.value == pytest.approx(0.25)
    assert not tw.finished
    tw.update(10)
    assert tw.value == 1.0
    assert tw.finished


def test_tween_com_atraso():
    tw = Tween(1.0, linear, delay=0.5)
    tw.update(0.4)
    assert not tw.started
    assert tw.value == 0.0
    tw.update(0.6)
    assert tw.value == pytest.approx(0.5)


def test_tween_reset_e_finish():
    tw = Tween(0.3)
    tw.finish()
    assert tw.finished
    tw.reset()
    assert tw.value == 0.0


def test_duracao_invalida():
    with pytest.raises(ValueError):
        Tween(0)
