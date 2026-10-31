# -*- coding: utf-8 -*-
from pathlib import Path

p = Path("10-pvz/pvz_graphics.py")
text = p.read_text(encoding="utf-8")

old_block = """    # 原版尺寸映射与微缩放适配
    base_w, base_h = frame.get_size()
    target_h = int(88 * scale)
    y_offset = 2 * scale
    if plant_type == "spikeweed":
        target_h = int(46 * scale)
        y_offset = 22 * scale
    elif plant_type == "lilypad":
        target_h = int(40 * scale)
        y_offset = 24 * scale"""

new_block = """    # 原版尺寸映射与微缩放适配
    base_w, base_h = frame.get_size()
    target_h = int(88 * scale)
    target_w = None
    y_offset = 2 * scale
    if plant_type == "spikeweed":
        target_h = int(46 * scale)
        y_offset = 22 * scale
    elif plant_type == "lilypad":
        target_h = int(72 * scale)
        target_w = int(112 * scale)
        y_offset = 22 * scale"""

assert old_block in text, "old_block not found!"
text = text.replace(old_block, new_block)

old_catapult = """    elif plant_type in ("cabbagepult", "kernelpult"):
        target_h = int(92 * scale)
        y_offset = 2 * scale
    elif plant_type in ("melonpult", "wintermelon"):
        target_h = int(96 * scale)
        y_offset = 0 * scale
    elif plant_type == "threepeater":
        target_h = int(96 * scale)
    ratio = target_h / max(1, base_h)
    target_w = int(base_w * ratio)"""

new_catapult = """    elif plant_type in ("cabbagepult", "kernelpult"):
        target_h = int(88 * scale)
        y_offset = 4 * scale
    elif plant_type in ("melonpult", "wintermelon"):
        target_h = int(98 * scale)
        y_offset = -2 * scale
    elif plant_type == "threepeater":
        target_h = int(96 * scale)
    if target_w is None:
        ratio = target_h / max(1, base_h)
        target_w = int(base_w * ratio)"""

assert old_catapult in text, "old_catapult not found!"
text = text.replace(old_catapult, new_catapult)

p.write_text(text, encoding="utf-8")
print("SUCCESSFULLY_UPDATED_PVZ_GRAPHICS")
