# -*- coding: utf-8 -*-
from pathlib import Path

path = Path("10-pvz/pvz_ten_levels.py")
with open(path, "r", encoding="utf-8") as f:
    code = f.read()

target = """    def _update_visuals(self, dt: float) -> None:
        for token in self.suns:
            if not token.collected:
                token.update(dt)"""

replacement = """    def _update_visuals(self, dt: float) -> None:
        # 自动收集阳光检测 (第 10 关通关后解锁，用户可随时开/关)
        if getattr(self, "auto_sun_unlocked", False) and getattr(self, "auto_sun_enabled", True):
            for token in self.suns:
                if not token.collected and token.age >= 0.25:
                    self.collect_sun(token)

        for token in self.suns:
            if not token.collected:
                token.update(dt)"""

assert target in code, "Target not found in _update_visuals"
code = code.replace(target, replacement, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

print("Updated _update_visuals with auto_sun logic successfully!")
