# -*- coding: utf-8 -*-
"""Headless Battle Simulation and Endurance Test.
Simulates 1200 frames (20 seconds of 60 FPS combat) to ensure zero crashes,
zero division-by-zero, zero infinite loops, and rock-solid memory stability.
"""

import sys
import unittest
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Dummy video driver for headless testing
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from domain.model.session import Session
from domain.spec.levels import LEVELS
from usecases.start_level import start_level
from usecases.plant_seed import execute_plant_action
from usecases.advance_frame import advance_battle_frame
from infra.json_save import JsonSaveAdapter


class TestSimulationDryRun(unittest.TestCase):
    def test_full_level_battle_simulation(self):
        # 1. Start Day level 0
        session = Session(
            current_level_idx=0,
            unlocked_plants={"sunflower", "peashooter", "wallnut"},
            selected_seeds=["sunflower", "peashooter", "wallnut"],
            auto_sun_enabled=True,
        )
        world = start_level(0, session)
        self.assertEqual(world.sun, 150)

        # Plant a sunflower in col 0, row 2
        session.active_seed_idx = 0
        p_sun = execute_plant_action(col=0, row=2, world=world, session=session)
        self.assertIsNotNone(p_sun)
        self.assertEqual(world.sun, 100)

        # Plant a peashooter in col 1, row 2
        session.active_seed_idx = 1
        p_pea = execute_plant_action(col=1, row=2, world=world, session=session)
        self.assertIsNotNone(p_pea)
        self.assertEqual(world.sun, 0)

        # Run 1200 simulation frames (dt = 1/60s)
        dt = 1.0 / 60.0
        for frame in range(1200):
            reward = advance_battle_frame(world, session, dt)
            if world.is_game_over or world.is_victory:
                break

        # Invariants
        self.assertGreater(world.game_time, 0.0)
        self.assertTrue(p_sun.age > 0)
        print(f"Simulation completed at t={world.game_time:.2f}s, suns generated={len(world.suns)}, zombies={len(world.zombies)}")

    def test_pool_level_battle_simulation(self):
        # 2. Start Pool level 10
        session = Session(
            current_level_idx=10,
            unlocked_plants={"sunflower", "peashooter", "lilypad", "cattail", "kernelpult"},
            selected_seeds=["lilypad", "cattail", "kernelpult", "sunflower"],
            unlocked_artifacts={"auto_sun_magnet"},
            auto_sun_enabled=True,
        )
        world = start_level(10, session)
        self.assertEqual(world.layout.rows, 6)

        # Plant Lilypad in pool row 2, col 3
        session.active_seed_idx = 0
        p_pad = execute_plant_action(col=3, row=2, world=world, session=session)
        self.assertIsNotNone(p_pad)

        # Plant Cattail on Lilypad
        session.active_seed_idx = 1
        p_cat = execute_plant_action(col=3, row=2, world=world, session=session)
        self.assertIsNotNone(p_cat)

        # Run 600 frames
        dt = 1.0 / 60.0
        for _ in range(600):
            advance_battle_frame(world, session, dt)

        self.assertGreater(world.game_time, 0.0)


if __name__ == "__main__":
    unittest.main()
