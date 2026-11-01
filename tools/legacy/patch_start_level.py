# -*- coding: utf-8 -*-
from pathlib import Path

path = Path("10-pvz/pvz_ten_levels.py")
with open(path, "r", encoding="utf-8") as f:
    code = f.read()

target = """        self.save_data = load_save()
        self.artifacts = set(self.save_data.get("artifacts", [])).union(getattr(self, "artifacts", set()))
        self.slot_capacity = 10 if "master_belt" in self.artifacts else 9
        self._reset_runtime()"""

replacement = """        self.save_data = load_save()
        self.artifacts = set(self.save_data.get("artifacts", [])).union(getattr(self, "artifacts", set()))
        self.slot_capacity = 10 if "master_belt" in self.artifacts else 9
        self._reset_runtime()
        self.auto_sun_unlocked = bool("auto_sun_magnet" in self.artifacts or self.save_data.get("highest_level", 0) >= 9 or self.level_index >= 9)"""

assert target in code, "Target not found in start_level"
code = code.replace(target, replacement, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

print("Updated start_level with auto_sun_unlocked check successfully!")
