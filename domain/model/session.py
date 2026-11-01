# -*- coding: utf-8 -*-
"""Session and Progress model.
Tracks career progress, unlocked plants/artifacts, seed selections, and options.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Session:
    current_level_idx: int = 0
    highest_level: int = 0
    unlocked_plants: set[str] = field(default_factory=lambda: {"sunflower", "peashooter"})
    unlocked_artifacts: set[str] = field(default_factory=set)
    endless_best_wave: int = 0

    # User preferences
    auto_sun_enabled: bool = True
    speed_multiplier: float = 1.0
    sound_enabled: bool = True
    music_enabled: bool = True
    is_fullscreen: bool = False

    # In-match ephemeral selection state
    selected_seeds: list[str] = field(default_factory=list)
    seed_cooldowns: dict[str, float] = field(default_factory=dict)
    active_seed_idx: Optional[int] = None
    active_shovel: bool = False
    game_mode: str = "menu"
    cob_targeting_col_row: Optional[tuple[int, int]] = None

    @property
    def max_seed_slots(self) -> int:
        return 10 if "master_belt" in self.unlocked_artifacts else 8

    @property
    def has_auto_sun(self) -> bool:
        """True if the player has unlocked the magnet artifact."""
        return "auto_sun_magnet" in self.unlocked_artifacts or self.highest_level >= 10
