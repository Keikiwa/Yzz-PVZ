# -*- coding: utf-8 -*-
"""Projectile entity model.
Handles both horizontal ballistic projectiles and parabolic lobbed projectiles.
"""

from dataclasses import dataclass
from typing import Optional


_PROJECTILE_ID_COUNTER = 0


def next_projectile_id() -> int:
    global _PROJECTILE_ID_COUNTER
    _PROJECTILE_ID_COUNTER += 1
    return _PROJECTILE_ID_COUNTER


@dataclass
class Projectile:
    id: int
    bullet_type: str
    row: int
    x: float
    y: float
    damage: float
    vx: float = 340.0
    vy: float = 0.0

    # Lobbed trajectory state
    is_lobbed: bool = False
    start_x: float = 0.0
    start_y: float = 0.0
    target_x: float = 0.0
    target_y: float = 0.0
    arc_height: float = 140.0
    flight_t: float = 0.0
    flight_duration: float = 0.85

    # Homing & Guidance
    homing: bool = False
    target_zombie_id: Optional[int] = None

    # Piercing & Range
    piercing: bool = False
    hit_zombie_ids: set[int] = None
    range_traveled: float = 0.0
    max_range: float = 2000.0
    alive: bool = True

    def __post_init__(self):
        if self.hit_zombie_ids is None:
            self.hit_zombie_ids = set()

    @classmethod
    def create_straight(
        cls, bullet_type: str, row: int, x: float, y: float, damage: float,
        vx: float = 340.0, vy: float = 0.0, max_range: float = 2000.0, piercing: bool = False,
    ) -> "Projectile":
        return cls(
            id=next_projectile_id(),
            bullet_type=bullet_type,
            row=row,
            x=x,
            y=y,
            damage=damage,
            vx=vx,
            vy=vy,
            max_range=max_range,
            piercing=piercing,
        )

    @classmethod
    def create_lobbed(
        cls, bullet_type: str, row: int, start_x: float, start_y: float,
        target_x: float, target_y: float, damage: float, arc_height: float = 130.0, duration: float = 0.8,
    ) -> "Projectile":
        return cls(
            id=next_projectile_id(),
            bullet_type=bullet_type,
            row=row,
            x=start_x,
            y=start_y,
            damage=damage,
            is_lobbed=True,
            start_x=start_x,
            start_y=start_y,
            target_x=target_x,
            target_y=target_y,
            arc_height=arc_height,
            flight_t=0.0,
            flight_duration=duration,
        )

    @classmethod
    def create_homing(
        cls, bullet_type: str, row: int, x: float, y: float, damage: float, target_zombie_id: Optional[int] = None,
    ) -> "Projectile":
        return cls(
            id=next_projectile_id(),
            bullet_type=bullet_type,
            row=row,
            x=x,
            y=y,
            damage=damage,
            vx=300.0,
            homing=True,
            target_zombie_id=target_zombie_id,
        )
