# -*- coding: utf-8 -*-
"""Wave state and pacing model."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class WaveState:
    level_id: int
    total_zombies: int
    spawned_count: int = 0
    killed_count: int = 0
    wave_index: int = 0
    total_waves: int = 2
    timer_until_next_wave: float = 18.0
    pending_spawns: list[dict] = field(default_factory=list)
    initial_total_hp: float = 1.0
    is_wave_active: bool = False
    huge_wave_warning: bool = False
    warning_timer: float = 0.0

    @property
    def is_all_spawned(self) -> bool:
        return self.spawned_count >= self.total_zombies and len(self.pending_spawns) == 0

    @property
    def progress_ratio(self) -> float:
        if self.total_zombies <= 0:
            return 1.0
        return min(1.0, max(0.0, self.killed_count / self.total_zombies))
