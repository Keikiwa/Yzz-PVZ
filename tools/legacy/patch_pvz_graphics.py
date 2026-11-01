# -*- coding: utf-8 -*-
import os

path = r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\pvz_graphics.py"
with open(path, "r", encoding="utf-8") as f:
    code = f.read()

target1 = """    if plant_type == 'tallnut':
        actions = _PLANT_FRAMES.get('wallnut')
    elif plant_type == 'gatlingpea':
        actions = _PLANT_FRAMES.get('repeater')
    else:
        actions = _PLANT_FRAMES.get(plant_type)"""

replacement1 = """    actions = _PLANT_FRAMES.get(plant_type)
    if not actions:
        if plant_type == 'tallnut':
            actions = _PLANT_FRAMES.get('wallnut')
        elif plant_type == 'gatlingpea':
            actions = _PLANT_FRAMES.get('repeater')"""

target2 = """    if plant_type == "wallnut":"""

replacement2 = """    if plant_type in ("wallnut", "tallnut"):"""

target3 = """    elif plant_type == "cattail":
        if plant and getattr(plant, "attacking", False) and "attack" in actions:
            action_key = "attack"
            fps = 12.0"""

replacement3 = """    elif plant_type == "cattail":
        if plant and getattr(plant, "attacking", False) and "attack" in actions:
            action_key = "attack"
            fps = 12.0
    elif plant_type == "fumeshroom":
        if plant and getattr(plant, "shooting", 0) > 0 and "attack" in actions:
            action_key = "attack"
            fps = 10.0
    elif plant_type == "laserbean":
        if plant and getattr(plant, "shooting", 0) > 0 and "attack" in actions:
            action_key = "attack"
            fps = 14.0"""

target4 = """    elif plant_type in ("hypnoshroom", "fumeshroom"):
        target_h = int(72 * scale)
        y_offset = 8 * scale"""

replacement4 = """    elif plant_type == "fumeshroom":
        target_h = int(82 * scale)
        y_offset = 4 * scale
    elif plant_type == "hypnoshroom":
        target_h = int(76 * scale)
        y_offset = 6 * scale
    elif plant_type == "laserbean":
        target_h = int(84 * scale)
        y_offset = 2 * scale
    elif plant_type == "magicshroom":
        target_h = int(82 * scale)
        y_offset = 4 * scale
    elif plant_type == "agave":
        target_h = int(90 * scale)
        y_offset = 0 * scale"""

assert target1 in code, "target1 not found"
assert target2 in code, "target2 not found"
assert target3 in code, "target3 not found"
assert target4 in code, "target4 not found"

code = code.replace(target1, replacement1, 1)
code = code.replace(target2, replacement2, 1)
code = code.replace(target3, replacement3, 1)
code = code.replace(target4, replacement4, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

print("Successfully patched pvz_graphics.py!")
