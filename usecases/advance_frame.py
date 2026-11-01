# -*- coding: utf-8 -*-
"""Frame advance use case.
Drives a single deterministic battle simulation tick.
"""

from typing import Optional
from domain.model.world import World
from domain.model.session import Session
from domain.spec.rewards import LevelReward
from domain.rules.economy import update_economy
from domain.rules.combat import update_combat
from domain.rules.projectile_rules import update_projectiles
from domain.rules.progress import check_progress


def advance_battle_frame(world: World, session: Session, dt: float) -> Optional[LevelReward]:
    # Factor in speed multiplier
    effective_dt = dt * session.speed_multiplier

    # 1. Update card cooldowns
    for seed, cd in list(session.seed_cooldowns.items()):
        if cd > 0:
            session.seed_cooldowns[seed] = max(0.0, cd - effective_dt)

    # 2. Update screen shake
    world.shake.update(effective_dt)

    # 3. Spatial indexing for ultra-fast O(1) lane queries
    world.rebuild_spatial_index()

    # 4. Economy update (sun drops, magnet auto-suction, collection animations)
    update_economy(world, session, effective_dt)

    # 5. Combat update (plants attack, zombies march, hypno brawls, mowers)
    update_combat(world, session, effective_dt)

    # 6. Projectiles kinematics and impacts
    update_projectiles(world, effective_dt)

    # 7. Check game over and victory conditions
    reward = check_progress(world, session, effective_dt)

    # 8. Update floating texts and particles
    for ft in world.floating_texts:
        ft.age += effective_dt
        ft.y += ft.vy * effective_dt

    for pt in world.particles:
        pt.age += effective_dt
        pt.x += pt.vx * effective_dt
        pt.y += pt.vy * effective_dt

    # 9. Clean up dead and expired entities
    world.remove_dead_entities()

    return reward
