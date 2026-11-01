# -*- coding: utf-8 -*-
"""Collect sun use case."""

from domain.model.world import World
from domain.rules.economy import collect_sun_at


def execute_collect_sun(mx: float, my: float, world: World) -> bool:
    return collect_sun_at(mx, my, world)
