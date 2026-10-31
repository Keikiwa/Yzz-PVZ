# -*- coding: utf-8 -*-
import os, sys
import pygame

sys.path.insert(0, r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz")
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
pygame.display.set_mode((1, 1))

import pvz_graphics
import pvz_ten_levels as game

pvz_graphics.init_graphics()

print("=== CHECKING _PLANT_FRAMES IN PVZ_GRAPHICS ===")
for k in game.PLANTS.keys():
    actions = pvz_graphics._PLANT_FRAMES.get(k)
    if actions:
        summary = ", ".join(f"{act}:{len(frames)}" for act, frames in actions.items())
        print(f"{k:18} | OK | {summary}")
    else:
        print(f"{k:18} | MISSING!")

print("\n=== RENDERING ALL 34 PLANTS ONTO TEST SURFACE ===")
test_surf = pygame.Surface((1200, 760), pygame.SRCALPHA)
success_count = 0
for idx, (k, v) in enumerate(game.PLANTS.items()):
    r = idx // 7
    c = idx % 7
    cx = 100 + c * 150
    cy = 100 + r * 130
    res = pvz_graphics.render_plant_sprite(
        surface=test_surf,
        plant_type=k,
        center=(cx, cy),
        scale=1.0,
        time_value=1.5,
        hp_ratio=1.0,
        age=10.0,
        plant=None
    )
    if res:
        success_count += 1
    else:
        print(f"FAILED to render plant: {k}")

print(f"Successfully rendered: {success_count}/{len(game.PLANTS)} plants!")
pygame.image.save(test_surf, r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\tools\test_rendered_plants_montage.png")
print("Saved tools/test_rendered_plants_montage.png")
