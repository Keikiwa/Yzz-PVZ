# -*- coding: utf-8 -*-
"""Test script for 5 new plants and water zombie restrictions."""

import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pygame
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
pygame.init()
screen = pygame.display.set_mode((1200, 760))

import pvz_ten_levels

def test_v3():
    print("=== 开始测试 V3 新植物与水生僵尸水域约束 ===")
    game = pvz_ten_levels.Game(screen, headless=True)

    # 1. 测试水生僵尸行约束
    print("\n--- 1. 测试水生僵尸严格限制在水路 ---")
    game.start_level(10) # 泳池第 11 关
    waves = game._build_waves()
    water_lanes = game.pool_rows
    land_lanes = [r for r in range(game.rows) if r not in water_lanes]
    for w_idx, wave in enumerate(waves):
        for m in wave.members:
            if m.ztype in ("ducky", "snorkel", "dolphin"):
                assert m.row in water_lanes, f"波次 {w_idx} 水生僵尸 {m.ztype} 错误出现在陆地第 {m.row} 行！"
            elif m.ztype in ("pole", "newspaper", "runner"):
                assert m.row in land_lanes, f"波次 {w_idx} 陆地专属僵尸 {m.ztype} 错误出现在水路第 {m.row} 行！"
    print("全部波次中水生僵尸 (ducky, snorkel, dolphin) 100% 仅出现在泳池水路中！(PASS)")

    # 2. 测试魅惑菇
    print("\n--- 2. 测试魅惑菇魅惑僵尸 ---")
    game.start_level(0)
    hypno = pvz_ten_levels.Plant("hypnoshroom", 3, 0, 300, 300, cell_h=game.cell_h)
    game.plants = [hypno]
    enemy_zombie = pvz_ten_levels.Zombie("bucket", 0, hypno.x + 20, 470, 470, 15.0, 34.0, cell_h=game.cell_h)
    game.zombies = [enemy_zombie]
    # Zombie attacks plant
    game._update_zombies(0.6)
    assert not hypno.alive, "魅惑菇被啃咬后应牺牲"
    assert getattr(enemy_zombie, "hypnotized", False), "僵尸应已被魅惑"
    assert enemy_zombie.speed < 0, f"魅惑僵尸移速应反转为负值向右行进，实际为 {enemy_zombie.speed}"
    print("魅惑菇生效：成功使僵尸倒戈掉头！(PASS)")

    # 3. 测试大喷菇穿透伤害
    print("\n--- 3. 测试大喷菇穿透伤害 ---")
    fume = pvz_ten_levels.Plant("fumeshroom", 1, 1, 300, 300, cell_h=game.cell_h)
    fume.action_timer = 2.0
    game.plants = [fume]
    z1 = pvz_ten_levels.Zombie("basic", 1, fume.x + 80, 170, 170, 0, 0, cell_h=game.cell_h)
    z2 = pvz_ten_levels.Zombie("basic", 1, fume.x + 160, 170, 170, 0, 0, cell_h=game.cell_h)
    game.zombies = [z1, z2]
    game.projectiles = []
    game._update_plants(0.1)
    assert len(game.projectiles) >= 1, "大喷菇应射出孢子气团"
    # Projectile moves through z1 and z2
    p = game.projectiles[0]
    game._update_projectiles(0.1)
    p.x = z1.x
    game._update_projectiles(0.01)
    p.x = z2.x
    game._update_projectiles(0.01)
    assert z1.hp < 170 and z2.hp < 170, "大喷菇穿透孢子应同时伤害多个僵尸"
    print("大喷菇生效：穿透孢子成功同时伤害一行内多个目标！(PASS)")

    # 4. 测试双子向日葵双倍阳光
    print("\n--- 4. 测试双子向日葵双倍阳光 ---")
    twin = pvz_ten_levels.Plant("twinsunflower", 0, 0, 300, 300, cell_h=game.cell_h)
    twin.action_timer = 10.0
    game.plants = [twin]
    game.suns = []
    game._update_plants(0.1)
    assert len(game.suns) == 2, f"双子向日葵应同时产生 2 枚阳光，实际为 {len(game.suns)}"
    print("双子向日葵生效：一次稳定产出 2 颗阳光（50阳光）！(PASS)")

    # 5. 测试杨桃 5 向射击
    print("\n--- 5. 测试杨桃 5 向弹幕 ---")
    star = pvz_ten_levels.Plant("starfruit", 2, 2, 300, 300, cell_h=game.cell_h)
    star.action_timer = 2.0
    game.plants = [star]
    game.zombies = [pvz_ten_levels.Zombie("basic", 0, 800, 100, 100, 0, 0, cell_h=game.cell_h)]
    game.projectiles = []
    game._update_plants(0.1)
    assert len(game.projectiles) == 5, f"杨桃应同时射出 5 枚飞星，实际为 {len(game.projectiles)}"
    print("杨桃生效：成功向 5 个方位齐射金星弹幕！(PASS)")

    # 6. 测试毁灭菇核爆
    print("\n--- 6. 测试毁灭菇末日核爆 ---")
    doom = pvz_ten_levels.Plant("doomshroom", 2, 2, 300, 300, cell_h=game.cell_h)
    doom.age = 1.1
    game.plants = [doom]
    z_close = pvz_ten_levels.Zombie("bucket", 2, doom.x + 80, 470, 470, 0, 0, cell_h=game.cell_h)
    z_far = pvz_ten_levels.Zombie("bucket", 2, doom.x + 500, 470, 470, 0, 0, cell_h=game.cell_h)
    game.zombies = [z_close, z_far]
    game._update_plants(0.1)
    assert not doom.alive, "毁灭菇核爆后应消失"
    assert z_close.dead, "近处僵尸应被 1800 巨额核爆瞬秒"
    assert not z_far.dead, "超出 5x5 范围的僵尸不受波及"
    print("毁灭菇生效：末日核爆成功瞬秒范围内所有敌人！(PASS)")

    print("\n=== 全部 V3 新机制测试 100% 通过！ ===")

if __name__ == "__main__":
    test_v3()
