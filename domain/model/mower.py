# -*- coding: utf-8 -*-
"""Lawnmower and Pool cleaner entity model."""

from dataclasses import dataclass


@dataclass
class Mower:
    row: int
    x: float
    y: float
    active: bool = True
    triggered: bool = False
    speed: float = 480.0
    is_pool: bool = False

    def trigger(self) -> None:
        if self.active and not self.triggered:
            self.triggered = True

    def update(self, dt: float) -> bool:
        """Moves mower if triggered. Returns False when rolled off-screen."""
        if not self.active:
            return False
        if self.triggered:
            self.x += self.speed * dt
            if self.x > 1300:
                self.active = False
                return False
        return True
