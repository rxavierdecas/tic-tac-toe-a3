"""Animações temporizadas: interpolação (tween) com funções de easing.

As animações avançam por `dt` (segundos desde o último quadro), o que as
torna independentes da taxa de quadros.
"""

from __future__ import annotations

import math
from collections.abc import Callable

Easing = Callable[[float], float]


def linear(t: float) -> float:
    return t


def ease_out_cubic(t: float) -> float:
    """Desacelera ao final: rápido no início, suave na chegada."""
    return 1 - (1 - t) ** 3


def ease_in_out_sine(t: float) -> float:
    return -(math.cos(math.pi * t) - 1) / 2


def ease_out_back(t: float, overshoot: float = 1.70158) -> float:
    """Ultrapassa levemente o destino e retorna (efeito "pop")."""
    c3 = overshoot + 1
    return 1 + c3 * (t - 1) ** 3 + overshoot * (t - 1) ** 2


class Tween:
    """Progresso normalizado de 0 a 1 ao longo de `duration` segundos."""

    def __init__(self, duration: float, easing: Easing = ease_out_cubic, delay: float = 0.0):
        if duration <= 0:
            raise ValueError("A duração deve ser positiva")
        self.duration = duration
        self.easing = easing
        self.delay = delay
        self.time = 0.0

    def update(self, dt: float) -> None:
        self.time = min(self.time + dt, self.delay + self.duration)

    @property
    def raw(self) -> float:
        """Progresso linear (sem easing), limitado a [0, 1]."""
        t = (self.time - self.delay) / self.duration
        return max(0.0, min(1.0, t))

    @property
    def value(self) -> float:
        """Progresso com easing aplicado."""
        return self.easing(self.raw)

    @property
    def started(self) -> bool:
        return self.time > self.delay

    @property
    def finished(self) -> bool:
        return self.time >= self.delay + self.duration

    def finish(self) -> None:
        self.time = self.delay + self.duration

    def reset(self) -> None:
        self.time = 0.0
