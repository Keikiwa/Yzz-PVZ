# -*- coding: utf-8 -*-
"""Generate high-res screenshots for output showcase:
1. 泳池水面激战实机 (展示睡莲、猫尾草、玉米加农炮、巨人僵尸、气球僵尸、小鬼僵尸)
2. 34 种全植物选卡界面 (9列 x 4行 舒展排布，10格战术卡槽)
3. 通关神器奖励结算 (黄金阳光铲与新植物解锁)
"""

import os
import sys
from pathlib import Path

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
pygame.init()
screen = pygame.display.set_mode((1200, 760))

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pvz_ten_levels

OUT_DIR = Path(r"F:\Desktop\.DeskBox\文件夹\反重力产出\图片")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_screenshots():
    print("=== 开始生成 V5 高清交付预览截图 ===")
    game = pvz_ten_levels.Game(screen, headless=True)

    # 1. 泳池实战大图 (Level 11 泳池水面激战，加入巨人僵尸、气球僵尸与玉米加农炮)
    game.setup_preview(10) # 第 11 关泳池
    # 放置玉米加农炮 (col 0, row 1)
    cannon = pvz_ten_levels.Plant("cobcannon", 0, 1, 1200, 1200, cell_h=game.cell_h)
    game.plants.append(cannon)
    # 放置魔术菇 (col 1, row 4)
    magic = pvz_ten_levels.Plant("magicshroom", 1, 4, 300, 300, cell_h=game.cell_h)
    game.plants.append(magic)
    # 放置龙舌兰 (col 3, row 0)
    agave = pvz_ten_levels.Plant("agave", 3, 0, 600, 600, cell_h=game.cell_h)
    game.plants.append(agave)

    # 迎战巨人僵尸、气球僵尸、小鬼僵尸
    garg = pvz_ten_levels.Zombie("gargantuar", 4, 760, 3000, 3000, 11.0, 1500, cell_h=game.cell_h)
    balloon = pvz_ten_levels.Zombie("balloon", 1, 710, 140, 140, 17.0, 28, cell_h=game.cell_h)
    imp = pvz_ten_levels.Zombie("imp", 4, 620, 90, 90, 38.0, 25, cell_h=game.cell_h)
    game.zombies.extend([garg, balloon, imp])

    for _ in range(30):
        game.time_value += 1 / 60
        game.update(1 / 60)
    game.banner_timer = 0
    game.wave_flash = 0
    game.draw()
    shot1 = OUT_DIR / "植物大战僵尸_泳池水面激战实机.png"
    pygame.image.save(screen, str(shot1))
    print(f"1. 泳池实战图已保存: {shot1}")

    # 2. 选卡界面大图 (34 种全植物 9列 x 4行，10格战术卡槽)
    game.start_level(15) # 无尽挑战选卡
    game.mode = "seed_select"
    game.slot_capacity = 10
    game.selected_seeds = [
        "sunflower", "lilypad", "cobcannon", "cattail",
        "magicshroom", "agave", "laserbean", "wintermelon", "gatlingpea", "wallnut"
    ]
    for _ in range(15):
        game.time_value += 1 / 60
        game.draw()
    shot2 = OUT_DIR / "植物大战僵尸_全植物选卡界面.png"
    pygame.image.save(screen, str(shot2))
    print(f"2. 选卡界面图已保存: {shot2}")

    # 3. 第 5 关通关黄金阳光铲结算弹窗大图
    game.start_level(4)
    game.overlay = "won"
    game.overlay_age = 1.8
    for _ in range(15):
        game.time_value += 1 / 60
        game.draw()
    shot3 = OUT_DIR / "植物大战僵尸_通关神器奖励结算.png"
    pygame.image.save(screen, str(shot3))
    print(f"3. 奖励结算图已保存: {shot3}")

    print("=== 全部预览截图生成完毕 ===")

if __name__ == "__main__":
    generate_screenshots()
