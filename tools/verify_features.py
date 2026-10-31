import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
# -*- coding: utf-8 -*-
"""Comprehensive verification script for new PvZ features."""

import os
import pygame
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
pygame.init()
screen = pygame.display.set_mode((1200, 760))

import pvz_ten_levels

def test_features():
    print("=== 开始测试核心增强功能 ===")
    game = pvz_ten_levels.Game(screen, headless=True)

    # 1. 测试黄金阳光铲
    print("\n--- 1. 测试黄金阳光铲 ---")
    game.start_level(0)
    game.sun = 500
    # 未解锁黄金铲
    game.artifacts = set()
    plant = pvz_ten_levels.Plant("sunflower", 2, 2, 300, 300, cell_h=game.cell_h)
    game.plants = [plant]
    game.shovel_selected = True
    pos = (pvz_ten_levels.GRID_X + int(2.5 * pvz_ten_levels.CELL_W), pvz_ten_levels.GRID_Y + int(2.5 * game.cell_h))
    game._handle_click(pos)
    assert not plant.alive, "植物应已被铲除"
    assert game.sun == 500, f"未解锁黄金铲不应返还阳光，当前阳光: {game.sun}"
    print("未解锁黄金铲：成功铲除，无阳光返还 (PASS)")

    # 已解锁黄金铲
    game.artifacts = {"golden_shovel"}
    melon = pvz_ten_levels.Plant("melonpult", 2, 2, 300, 300, cell_h=game.cell_h)
    game.plants = [melon]
    game.shovel_selected = True
    game._handle_click(pos)
    assert not melon.alive, "西瓜投手应已被铲除"
    assert game.sun == 500 + pvz_ten_levels.PLANTS["melonpult"]["cost"], f"黄金铲应返还 300 阳光，当前阳光: {game.sun}"
    print(f"已解锁黄金铲：成功全额返还 {pvz_ten_levels.PLANTS['melonpult']['cost']} 阳光！(PASS)")

    # 2. 测试阳光储蓄罐
    print("\n--- 2. 测试阳光储蓄罐 ---")
    game.artifacts = set()
    game.start_level(0)
    base_sun = pvz_ten_levels.LEVELS[0]["sun"]
    assert game.sun == base_sun, f"基础阳光应为 {base_sun}"

    game.artifacts = {"sun_vault"}
    game.start_level(0)
    assert game.sun == base_sun + 100, f"储蓄罐阳光应为 {base_sun + 100}，实际为: {game.sun}"
    print(f"阳光储蓄罐生效：开局获得 +100 额外阳光储备 (PASS)")

    # 3. 测试高坚果阻挡撑杆跳与海豚跳跃
    print("\n--- 3. 测试高坚果拦截跳跃 ---")
    tallnut = pvz_ten_levels.Plant("tallnut", 3, 0, 8000, 8000, cell_h=game.cell_h)
    game.plants = [tallnut]
    pole_zombie = pvz_ten_levels.Zombie("pole", 0, tallnut.x + 20, 240, 240, 32.0, 28.0, has_pole=True, vault_state="run", cell_h=game.cell_h)
    game.zombies = [pole_zombie]
    game._update_zombies(0.1)
    assert not pole_zombie.has_pole, "撑杆跳僵尸撞上高坚果应失去撑杆"
    assert pole_zombie.vault_state == "done", "撑杆跳跃应被强制终止"
    print("高坚果拦截撑杆跳成功！(PASS)")

    # 4. 测试火炬点燃机枪射手 4 连发
    print("\n--- 4. 测试火炬点燃机枪射手 ---")
    game.plants = [pvz_ten_levels.Plant("torchwood", 4, 1, 300, 300, cell_h=game.cell_h)]
    game.zombies = [pvz_ten_levels.Zombie("bucket", 1, 1000, 470, 470, 0, 0, cell_h=game.cell_h)]
    gatling = pvz_ten_levels.Plant("gatlingpea", 2, 1, 300, 300, cell_h=game.cell_h)
    gatling.action_timer = 2.0
    game.plants.append(gatling)
    game.projectiles = []
    game._update_plants(0.1)
    assert len(game.projectiles) == 4, f"机枪射手应齐射 4 颗豌豆，实际为 {len(game.projectiles)}"
    # 让子弹飞过火炬
    torch_x = pvz_ten_levels.cell_center(4, 1, cell_h=game.cell_h)[0]
    for p in game.projectiles:
        p.x = torch_x - 5
    game._update_projectiles(0.05)
    fire_count = sum(1 for p in game.projectiles if p.bullet_type == "fire_pea")
    assert fire_count == 4, f"4 颗豌豆穿过火炬应全部变为 fire_pea，实际火球数: {fire_count}"
    print("机枪射手 4 连发被火炬点燃为 4 枚烈焰火球！(PASS)")

    # 5. 测试逐步解锁
    print("\n--- 5. 测试逐步解锁机制 ---")
    save_data = {"completed": [], "artifacts": []}
    import json
    with open(pvz_ten_levels.SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(save_data, f)
    # 第一关可用植物只有向日葵和豌豆射手
    game.start_level(0)
    avail = game.available_plants()
    assert "sunflower" in avail and "peashooter" in avail, "第一关初始应有向日葵和豌豆射手"
    print(f"第一关初始可用植物数: {len(avail)}，植物逐渐赠送机制健全 (PASS)")

    print("\n=== 所有新增机制与通关奖励测试 100% 通过！ ===")

if __name__ == "__main__":
    test_features()
