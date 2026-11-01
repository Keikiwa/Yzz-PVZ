# -*- coding: utf-8 -*-
"""Wave builder and level pacing rules.
Pure generation of timed spawn queues respecting land/pool lane constraints.
"""

import random
from typing import Optional
from domain.spec.levels import LevelSpec
from domain.spec.zombies import ZOMBIES
from domain.model.wave import WaveState


def build_level_waves(level: LevelSpec, rng: Optional[random.Random] = None) -> WaveState:
    if rng is None:
        rng = random.Random()

    total_count = level.zombie_count
    state = WaveState(level_id=level.id, total_zombies=total_count)

    # Weights normalization
    zombie_types = list(level.zombie_weights.keys())
    weights = list(level.zombie_weights.values())

    layout = level.layout
    water_rows = sorted(list(layout.pool_rows)) if level.is_pool else []
    land_rows = [r for r in range(layout.rows) if r not in water_rows]

    # Staggered wave groups
    current_time = 14.0  # Initial peaceful time before first zombie appears
    spawn_queue = []

    for i in range(total_count):
        z_type = rng.choices(zombie_types, weights=weights, k=1)[0]
        z_spec = ZOMBIES[z_type]

        # Respect water/land lane constraints
        if z_spec.is_water and water_rows:
            target_row = rng.choice(water_rows)
        else:
            target_row = rng.choice(land_rows) if land_rows else rng.choice(water_rows)

        # Spacing: early zombies trickle in; later ones come in dense swarms
        if i < 4:
            current_time += rng.uniform(8.0, 12.0)
        elif i == int(total_count * 0.5):
            current_time += 15.0  # Slight pause before mid-wave surge
        else:
            current_time += rng.uniform(2.5, 6.0)

        spawn_queue.append({
            "spawn_time": current_time,
            "spec_id": z_type,
            "row": target_row,
        })

    state.pending_spawns = spawn_queue
    return state


def generate_endless_wave(wave_num: int, rng: Optional[random.Random] = None) -> list[dict]:
    """Generates an escalating wave for Endless mode."""
    if rng is None:
        rng = random.Random()

    count = 12 + wave_num * 5
    z_types = ["basic", "cone", "bucket", "runner", "pole", "newspaper", "ducky", "snorkel", "dolphin"]
    if wave_num >= 3:
        z_types.append("gargantuar")

    spawns = []
    base_t = 10.0
    for _ in range(count):
        z_type = rng.choice(z_types)
        z_spec = ZOMBIES[z_type]
        row = rng.choice([2, 3]) if z_spec.is_water else rng.choice([0, 1, 4, 5])
        base_t += rng.uniform(1.5, 4.0)
        spawns.append({
            "spawn_time": base_t,
            "spec_id": z_type,
            "row": row,
        })
    return spawns
