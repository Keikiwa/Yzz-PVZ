# -*- coding: utf-8 -*-
"""Backward Compatibility Façade for pvz_ten_levels.py.
Forwards execution to the modular Clean Architecture entry point (main.py).
Retains classic spec definitions for legacy tools and test scripts.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Re-export core specs for legacy tests and tool compatibility
from domain.spec.plants import PLANTS
from domain.spec.zombies import ZOMBIES
from domain.spec.levels import LEVELS
from domain.spec.rewards import LEVEL_REWARDS, UNLOCK_ORDER
from domain.spec.artifacts import ARTIFACTS
from domain.spec.field_layout import FieldLayout, LAND_LAYOUT, POOL_LAYOUT
from app.game_loop import GameApp
from main import main

if __name__ == "__main__":
    main()
