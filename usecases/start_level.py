# -*- coding: utf-8 -*-
"""Start level use case.
Prepares the battlefield, layout, mowers, initial sun, and wave pacing for the selected level.
"""

from domain.model.world import World
from domain.model.session import Session
from domain.model.mower import Mower
from domain.spec.levels import LEVELS, LevelSpec
from domain.rules.wave_builder import build_level_waves


def start_level(level_idx: int, session: Session) -> World:
    level_idx = max(0, min(len(LEVELS) - 1, level_idx))
    level = LEVELS[level_idx]
    session.current_level_idx = level_idx

    layout = level.layout

    # Calculate initial sun (includes sun vault artifact bonus)
    initial_sun = level.initial_sun
    if "sun_vault" in session.unlocked_artifacts:
        initial_sun += 100

    # Initialize mowers for each lane
    mowers = []
    for r in range(layout.rows):
        is_pool_mower = level.is_pool and (r in layout.pool_rows)
        mowers.append(Mower(row=r, x=layout.grid_x - 30, y=layout.get_row_center_y(r), is_pool=is_pool_mower))

    # Build wave state
    wave_state = build_level_waves(level)

    world = World(
        layout=layout,
        mowers=mowers,
        wave_state=wave_state,
        sun=initial_sun,
    )
    world.rebuild_spatial_index()

    # Reset cooldowns
    session.seed_cooldowns = {p: 0.0 for p in session.selected_seeds}
    session.active_seed_idx = None
    session.active_shovel = False

    return world
