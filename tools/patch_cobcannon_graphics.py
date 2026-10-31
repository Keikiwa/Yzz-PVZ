# -*- coding: utf-8 -*-
import os

path = r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\pvz_graphics.py"
with open(path, "r", encoding="utf-8") as f:
    code = f.read()

target1 = """    frames = actions.get(action_key) or actions.get("idle")"""
replacement1 = """    frames = actions.get(action_key) or actions.get("idle") or (list(actions.values())[0] if actions else None)"""

target2 = """    elif plant_type == "agave":
        target_h = int(90 * scale)
        y_offset = 0 * scale"""
replacement2 = """    elif plant_type == "agave":
        target_h = int(90 * scale)
        y_offset = 0 * scale
    elif plant_type == "cobcannon":
        target_h = int(105 * scale)
        target_w = int(160 * scale)
        y_offset = -6 * scale"""

assert target1 in code, "target1 not found"
assert target2 in code, "target2 not found"

code = code.replace(target1, replacement1, 1)
code = code.replace(target2, replacement2, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

print("Updated pvz_graphics.py with cobcannon sizing and fallback frames!")
