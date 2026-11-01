# -*- coding: utf-8 -*-
"""Sun economy and generation rules.
Manages sky drop cadence, plant yields, manual click collection, and auto-collection.
"""

import random
from domain.model.world import World
from domain.model.session import Session
from domain.model.sun import Sun
from domain.model.particle import FloatingText
from domain.spec.math_util import lerp


def update_economy(world: World, session: Session, dt: float, is_night: bool = False) -> None:
    # 1. Natural sun cadence
    interval = 15.0 if is_night else 8.5
    world.natural_sun_timer -= dt
    if world.natural_sun_timer <= 0:
        world.natural_sun_timer = interval
        # Spawn random natural sun
        drop_x = random.uniform(world.layout.grid_x + 50, world.layout.grid_right - 50)
        target_row = random.randint(0, world.layout.rows - 1)
        target_y = world.layout.get_row_center_y(target_row)
        world.suns.append(Sun.create_sky(drop_x, -40, target_y, value=25))

    # 2. Update all active suns
    hud_counter_x = 75.0
    hud_counter_y = 42.0

    auto_magnet = session.has_auto_sun and session.auto_sun_enabled

    for s in world.suns:
        s.age += dt

        # Auto-collect magnet feature
        if auto_magnet and s.state != "collecting" and s.age >= 0.25:
            s.start_collect()

        if s.state == "falling":
            dy = s.target_y - s.y
            step = 140.0 * dt
            if dy <= step:
                s.y = s.target_y
                s.state = "landed"
            else:
                s.y += step

        elif s.state == "collecting":
            # Smooth cubic ease-in flight to top-left HUD counter
            s.collect_t += dt * 2.5
            t = min(1.0, s.collect_t)
            # Quadratic bezier curve with a slight upward arc
            control_x = (s.start_x + hud_counter_x) * 0.5
            control_y = min(s.start_y, hud_counter_y) - 60.0
            
            s.x = (1 - t) * (1 - t) * s.start_x + 2 * (1 - t) * t * control_x + t * t * hud_counter_x
            s.y = (1 - t) * (1 - t) * s.start_y + 2 * (1 - t) * t * control_y + t * t * hud_counter_y

            if t >= 1.0:
                s.state = "collected"
                world.sun += s.value
                world.floating_texts.append(
                    FloatingText(f"+{s.value}", hud_counter_x + 10, hud_counter_y + 15, (255, 235, 60))
                )


def collect_sun_at(mx: float, my: float, world: World) -> bool:
    """Manually clicks / hovers to collect a sun."""
    for s in world.suns:
        if s.contains(mx, my):
            s.start_collect()
            return True
    return False
