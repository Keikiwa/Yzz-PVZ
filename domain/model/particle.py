# -*- coding: utf-8 -*-
"""Combat visual effects, particles, floating texts, and screen shake."""

from dataclasses import dataclass
from typing import Optional
import random


@dataclass
class FloatingText:
    text: str
    x: float
    y: float
    color: tuple[int, int, int]
    lifetime: float = 0.8
    age: float = 0.0
    vy: float = -45.0

    @property
    def alive(self) -> bool:
        return self.age < self.lifetime

    @property
    def alpha(self) -> int:
        progress = self.age / self.lifetime
        return max(0, min(255, int(255 * (1.0 - progress))))


@dataclass
class CombatParticle:
    kind: str  # "splat", "butter", "ice", "spark", "ash"
    x: float
    y: float
    vx: float
    vy: float
    color: tuple[int, int, int]
    size: float
    lifetime: float
    age: float = 0.0

    @property
    def alive(self) -> bool:
        return self.age < self.lifetime


@dataclass
class ScreenShake:
    timer: float = 0.0
    duration: float = 0.0
    magnitude: float = 0.0

    def trigger(self, magnitude: float = 6.0, duration: float = 0.25) -> None:
        self.magnitude = max(self.magnitude, magnitude)
        self.duration = max(self.duration, duration)
        self.timer = self.duration

    def update(self, dt: float) -> tuple[float, float]:
        if self.timer <= 0:
            return 0.0, 0.0
        self.timer -= dt
        progress = self.timer / max(0.001, self.duration)
        current_mag = self.magnitude * progress
        ox = random.uniform(-current_mag, current_mag)
        oy = random.uniform(-current_mag, current_mag)
        return ox, oy
