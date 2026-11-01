# -*- coding: utf-8 -*-
"""Game configuration, display metrics, palettes, and filesystem paths.
Zero hardcoded absolute paths; strictly resolved relative to project root.
"""

from pathlib import Path

# Filesystem layout
BASE_DIR: Path = Path(__file__).resolve().parent.parent
ASSETS_DIR: Path = BASE_DIR / "assets"
SAVE_FILE: Path = BASE_DIR / "pvz_save.json"

# Audio paths
MUSIC_TRACKS: dict[str, Path] = {
    "menu": BASE_DIR / "music_menu.mp3",
    "day": BASE_DIR / "music_day.mp3",
    "night": BASE_DIR / "music_night.mp3",
    "seeds": BASE_DIR / "music_seeds.mp3",
    "endless": BASE_DIR / "music_endless.mp3",
}

# Display & Engine Constants
WIDTH: int = 1200
HEIGHT: int = 760
FPS: int = 60
HUD_H: int = 92

# Default Land Grid Geometry
GRID_X: int = 70
GRID_Y: int = 124
COLS: int = 9
ROWS: int = 5
CELL_W: int = 111
CELL_H: int = 116
GRID_RIGHT: int = GRID_X + COLS * CELL_W
GRID_BOTTOM: int = GRID_Y + ROWS * CELL_H

# Timers
NATURAL_SUN_INTERVAL: float = 8.5
FIRST_WAVE_DELAY: float = 18.0

# Color Palette
C_GOLD = (235, 185, 52)
C_SUN = (255, 230, 92)
C_CREAM = (248, 246, 233)
C_BROWN = (98, 62, 38)
C_GREEN = (92, 173, 63)
C_DARK = (31, 35, 28)
C_BLUE = (126, 214, 240)
C_RED = (226, 68, 54)
C_ICE = (168, 232, 255)
C_PURPLE = (180, 110, 220)
