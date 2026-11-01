# -*- coding: utf-8 -*-
"""Progress, victory, and defeat rules.
Handles wave spawn triggering, defeat boundary detection, victory resolution, and reward unlocks.
"""

from typing import Optional
from domain.model.world import World
from domain.model.session import Session
from domain.model.zombie import Zombie
from domain.spec.rewards import LEVEL_REWARDS, LevelReward


def check_progress(world: World, session: Session, dt: float) -> Optional[LevelReward]:
    world.game_time += dt

    # 1. Trigger pending spawns
    wave = world.wave_state
    remaining_spawns = []
    for sp in wave.pending_spawns:
        if world.game_time >= sp["spawn_time"]:
            # Spawn zombie!
            row = sp["row"]
            spawn_x = world.layout.grid_right + 50
            ground_y = world.layout.get_row_ground_y(row)
            new_zombie = Zombie.create(sp["spec_id"], row, spawn_x, ground_y)
            world.zombies.append(new_zombie)
            wave.spawned_count += 1
        else:
            remaining_spawns.append(sp)
    wave.pending_spawns = remaining_spawns

    # 2. Defeat check: any enemy zombie invaded past the threshold
    defeat_line = world.layout.grid_x - 35
    for z in world.zombies:
        if z.is_alive and not z.hypnotized and z.x < defeat_line:
            world.is_game_over = True
            return None

    # 3. Victory check: all spawned and all enemies eliminated
    alive_enemies = [z for z in world.zombies if z.is_alive and not z.hypnotized]
    wave.killed_count = wave.total_zombies - len(alive_enemies) - len(wave.pending_spawns)

    if wave.is_all_spawned and len(alive_enemies) == 0:
        world.is_victory = True
        reward = LEVEL_REWARDS.get(session.current_level_idx)
        if reward:
            for p in reward.plants:
                session.unlocked_plants.add(p)
            if reward.artifact:
                session.unlocked_artifacts.add(reward.artifact)

        if session.current_level_idx == session.highest_level:
            session.highest_level = min(15, session.highest_level + 1)

        return reward

    return None
