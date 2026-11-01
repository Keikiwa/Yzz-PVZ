# -*- coding: utf-8 -*-
from pathlib import Path

p = Path(r"10-pvz\pvz_ten_levels.py")
text = p.read_text(encoding="utf-8")

# 修复 handle_key 中的 else: 缩进
target = """            elif self.selected_plant or self.shovel_selected:
                self.selected_plant = None
                self.shovel_selected = False
        else:
                self.overlay = "paused"
                self.audio.pause_music()
            return"""

replacement = """            elif self.selected_plant or self.shovel_selected:
                self.selected_plant = None
                self.shovel_selected = False
            else:
                self.overlay = "paused"
                self.audio.pause_music()
            return"""

if target in text:
    text = text.replace(target, replacement)
    print("Fixed handle_key escape else indentation!")

p.write_text(text, encoding="utf-8")
print("clean_fix_all complete.")
