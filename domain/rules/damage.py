# -*- coding: utf-8 -*-
"""Combat damage authority.
Single source of truth for all damage calculations, armor mitigation,
bypass conditions, and status effect application.
"""

from typing import Optional
from domain.model.zombie import Zombie
from domain.model.particle import CombatParticle, FloatingText


def apply_damage(
    zombie: Zombie,
    amount: float,
    bypass_shield: bool = False,
    freeze_duration: float = 0.0,
    slow_duration: float = 0.0,
    butter_duration: float = 0.0,
    is_ash: bool = False,
) -> tuple[float, bool]:
    """Applies authoritative combat damage to a zombie.
    Returns (actual_damage_dealt, is_killed).
    """
    if not zombie.is_alive:
        return 0.0, False

    # Status effects
    if freeze_duration > 0:
        zombie.apply_freeze(freeze_duration)
    if slow_duration > 0:
        zombie.apply_slow(slow_duration)
    if butter_duration > 0:
        zombie.apply_butter(butter_duration)

    # Submerged check: if submerged and this is a normal projectile that cannot hit water,
    # it shouldn't hit (handled by projectile collision). If it reaches here, apply damage.
    if is_ash:
        # Instant incinerate (Cherry bomb, Jalapeno, Doom-shroom, Potato mine)
        dealt, _ = zombie.apply_damage(amount, bypass_shield=True)
        return dealt, not zombie.is_alive

    dealt, is_dead = zombie.apply_damage(amount, bypass_shield=bypass_shield)
    return dealt, is_dead
