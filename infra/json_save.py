# -*- coding: utf-8 -*-
"""JSON persistence adapter.
Implements SavePort with atomic writes to guarantee file integrity.
"""

import json
import os
from pathlib import Path
from typing import Any
from config.tuning import SAVE_FILE
from domain.model.session import Session


class JsonSaveAdapter:
    def __init__(self, file_path: Path = SAVE_FILE):
        self.file_path = file_path

    def load(self) -> Session:
        if not self.file_path.exists():
            return Session()

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            session = Session(
                current_level_idx=data.get("current_level", 0),
                highest_level=data.get("highest_level", data.get("level", 0)),
                unlocked_plants=set(data.get("unlocked_plants", ["sunflower", "peashooter"])),
                unlocked_artifacts=set(data.get("unlocked_artifacts", [])),
                endless_best_wave=data.get("endless_record", 0),
                auto_sun_enabled=data.get("auto_sun_enabled", True),
            )
            # Ensure basic plants are unlocked
            session.unlocked_plants.add("sunflower")
            session.unlocked_plants.add("peashooter")
            return session
        except Exception as e:
            print(f"Warning: Failed to load save file, fallback to default. Error: {e}")
            return Session()

    def save(self, session: Session) -> bool:
        data: dict[str, Any] = {
            "current_level": session.current_level_idx,
            "highest_level": session.highest_level,
            "level": session.highest_level,
            "unlocked_plants": sorted(list(session.unlocked_plants)),
            "unlocked_artifacts": sorted(list(session.unlocked_artifacts)),
            "endless_record": session.endless_best_wave,
            "auto_sun_enabled": session.auto_sun_enabled,
        }

        try:
            # Atomic write via temporary file
            temp_path = self.file_path.with_suffix(".tmp")
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(temp_path, self.file_path)
            return True
        except Exception as e:
            print(f"Error: Failed to save progress. Error: {e}")
            return False
