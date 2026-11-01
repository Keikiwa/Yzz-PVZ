# -*- coding: utf-8 -*-
from pathlib import Path

p = Path(r"10-pvz\pvz_ten_levels.py")
text = p.read_text(encoding="utf-8")

target = "def _handle_click(self, pos: tuple[int, int]) -> None:\n"
replacement = """def _handle_click(self, pos: tuple[int, int]) -> None:
        if self.overlay == "warp":
            if getattr(self, "warp_next_btn", None) and self.warp_next_btn.collidepoint(pos):
                next_lvl = (self.level_index + 1) % len(LEVELS)
                self.overlay = ""
                self.start_level(next_lvl)
                return
            if getattr(self, "warp_close_btn", None) and self.warp_close_btn.collidepoint(pos):
                self.overlay = ""
                return
            for wrect, idx in getattr(self, "warp_buttons", []):
                if wrect.collidepoint(pos):
                    self.overlay = ""
                    self.start_level(idx)
                    return
            return
"""

if target in text:
    text = text.replace(target, replacement, 1)
    p.write_text(text, encoding="utf-8")
    print("Successfully added warp handler to top of _handle_click!")
else:
    print("Target not found")
