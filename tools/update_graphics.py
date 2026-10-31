# -*- coding: utf-8 -*-
from pathlib import Path

p = Path("10-pvz/pvz_graphics.py")
s = p.read_text(encoding="utf-8")

old_actions = '''    actions = _PLANT_FRAMES.get(plant_type)
    if not actions:
        return False'''

new_actions = '''    if plant_type == 'tallnut':
        actions = _PLANT_FRAMES.get('wallnut')
    elif plant_type == 'gatlingpea':
        actions = _PLANT_FRAMES.get('repeater')
    else:
        actions = _PLANT_FRAMES.get(plant_type)
    if not actions:
        return False'''

s = s.replace(old_actions, new_actions, 1)

old_sizes = '''    elif plant_type == "torchwood":
        target_h = int(92 * scale)
        y_offset = -2 * scale'''

new_sizes = '''    elif plant_type == "tallnut":
        target_h = int(126 * scale)
        y_offset = -18 * scale
    elif plant_type == "gatlingpea":
        target_h = int(90 * scale)
        y_offset = 0 * scale
    elif plant_type == "torchwood":
        target_h = int(92 * scale)
        y_offset = -2 * scale'''

s = s.replace(old_sizes, new_sizes, 1)

old_post_render = '''    surface.blit(scaled, rect)
    return True'''

new_post_render = '''    surface.blit(scaled, rect)
    if plant_type == 'gatlingpea':
        helmet_rect = pygame.Rect(rect.centerx - 18 * scale, rect.y - 4 * scale, 36 * scale, 16 * scale)
        pygame.draw.ellipse(surface, (45, 78, 40), helmet_rect)
        pygame.draw.ellipse(surface, (70, 115, 60), helmet_rect.inflate(-4 * scale, -4 * scale))
        pygame.draw.line(surface, (30, 50, 25), (helmet_rect.left, helmet_rect.centery), (helmet_rect.right, helmet_rect.centery), max(1, int(2 * scale)))
    return True'''

s = s.replace(old_post_render, new_post_render, 1)
p.write_text(s, encoding="utf-8")
print("PVZ_GRAPHICS_UPDATED")
