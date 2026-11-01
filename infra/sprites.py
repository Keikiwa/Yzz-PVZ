# -*- coding: utf-8 -*-
"""Sprite and Graphics Adapter.
Connects the rendering pipeline with asset textures, procedural fallback drawings,
and cached surface lookups.
"""

from typing import Optional, Tuple
import pygame
import pvz_graphics


class SpriteBank:
    _instance = None

    def __init__(self):
        pvz_graphics.init_graphics()
        self._card_cache: dict[str, Optional[pygame.Surface]] = {}
        self._map_cache: dict[str, Optional[pygame.Surface]] = {}
        self._bullet_cache: dict[tuple[str, bool, int], Optional[pygame.Surface]] = {}

    @classmethod
    def get_instance(cls) -> "SpriteBank":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_card(self, plant_id: str, size: Optional[Tuple[int, int]] = (64, 82)) -> Optional[pygame.Surface]:
        key = f"{plant_id}_{size}"
        if key not in self._card_cache:
            self._card_cache[key] = pvz_graphics.get_card_surface(plant_id, target_size=size)
        return self._card_cache[key]

    def get_map(self, theme: str, size: Tuple[int, int] = (1200, 760)) -> Optional[pygame.Surface]:
        if theme not in self._map_cache:
            self._map_cache[theme] = pvz_graphics.get_map_surface(theme, target_size=size)
        return self._map_cache[theme]

    def get_mower(self, is_pool: bool = False, size: Tuple[int, int] = (64, 52)) -> Optional[pygame.Surface]:
        return pvz_graphics.get_mower_surface(target_size=size, is_pool=is_pool)

    def get_sun(self, time_val: float, radius: float = 24.0) -> Optional[pygame.Surface]:
        return pvz_graphics.get_sun_frame(time_val, radius=radius)

    def get_bullet(self, bullet_type: str = "pea", is_freeze: bool = False, size: int = 24) -> Optional[pygame.Surface]:
        key = (bullet_type, is_freeze, size)
        if key not in self._bullet_cache:
            self._bullet_cache[key] = pvz_graphics.get_bullet_surface(freeze=is_freeze, size=size, bullet_type=bullet_type)
        return self._bullet_cache[key]

    def render_plant(
        self, surface: pygame.Surface, plant_type: str, center: Tuple[float, float],
        scale: float, time_val: float, hp_ratio: float = 1.0, age: float = 10.0, plant: any = None,
    ) -> bool:
        return pvz_graphics.render_plant_sprite(surface, plant_type, center, scale, time_val, hp_ratio, age, plant)

    def render_zombie(
        self, surface: pygame.Surface, zombie: any, time_val: float, ground_y: float, alpha: int = 255, dy_offset: float = 0.0,
    ) -> bool:
        return pvz_graphics.render_zombie_sprite(surface, zombie, time_val, ground_y, alpha, dy_offset)


def get_sprites() -> SpriteBank:
    return SpriteBank.get_instance()
