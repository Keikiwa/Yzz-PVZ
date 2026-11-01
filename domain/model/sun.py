# -*- coding: utf-8 -*-
"""Sun token entity model.
Supports natural sky drop, plant pop, landing, and smooth magnetic suction towards HUD counter.
"""

from dataclasses import dataclass
import math


_SUN_ID_COUNTER = 0


def next_sun_id() -> int:
    global _SUN_ID_COUNTER
    _SUN_ID_COUNTER += 1
    return _SUN_ID_COUNTER


@dataclass
class Sun:
    id: int
    x: float
    y: float
    start_x: float
    start_y: float
    target_x: float
    target_y: float
    value: int = 25
    state: str = "falling"  # "falling", "landed", "collecting"
    age: float = 0.0
    lifetime: float = 12.0
    collect_t: float = 0.0
    radius: float = 34.0

    @classmethod
    def create_sky(cls, x: float, start_y: float, target_y: float, value: int = 25) -> "Sun":
        return cls(
            id=next_sun_id(),
            x=x,
            y=start_y,
            start_x=x,
            start_y=start_y,
            target_x=x,
            target_y=target_y,
            value=value,
            state="falling",
        )

    @classmethod
    def create_from_plant(cls, x: float, y: float, target_x: float, target_y: float, value: int = 25) -> "Sun":
        return cls(
            id=next_sun_id(),
            x=x,
            y=y,
            start_x=x,
            start_y=y,
            target_x=target_x,
            target_y=target_y,
            value=value,
            state="falling",
        )

    def contains(self, px: float, py: float) -> bool:
        if self.state == "collecting":
            return False
        dx = self.x - px
        dy = self.y - py
        return (dx * dx + dy * dy) <= (self.radius * self.radius)

    def start_collect(self) -> None:
        if self.state != "collecting":
            self.state = "collecting"
            self.start_x = self.x
            self.start_y = self.y
            self.collect_t = 0.0
