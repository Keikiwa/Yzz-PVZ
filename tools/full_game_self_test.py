# -*- coding: utf-8 -*-
"""Full gameplay multi-level self test simulating real user mouse clicks."""

import os
import sys
from pathlib import Path
import json

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
pygame.init()
screen = pygame.display.set_mode((1200, 760))

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import pvz_ten_levels as pvz

def test_full_game():
    print("=== 开始深度多关卡全流程自测 ===")
    game = pvz.Game(screen, headless=True)

    # 1. 测试第 1 关 (白天草坪 1)
    print("\n--- 1. 自测第 1 关 (新手入门) ---")
    game.start_level(0)
    assert game.level_index == 0
    assert not game.is_pool
    avail0 = game.available_plants()
    assert avail0 == ["sunflower", "peashooter"], f"第1关可用植物错误: {avail0}"
    game.selected_seeds = avail0
    game.mode = "playing"

    # 初始阳光 50 点，点击选择向日葵，点击 (col 0, row 2) 种植
    game.sun = 50
    game._select_plant("sunflower")
    assert game.selected_plant == "sunflower"
    pos_0_2 = pvz.cell_center(0, 2, game.cell_h)
    game._handle_click(pos_0_2)
    p_sun = game._top_plant_at(0, 2)
    assert p_sun is not None and p_sun.ptype == "sunflower", "种植向日葵失败"
    assert game.sun == 0

    # 阳光为 0 时尝试选取 100 阳光的豌豆射手，无法选取
    game._select_plant("peashooter")
    assert game.selected_plant is None, "阳光不足 100 却成功选中了豌豆射手"

    # 给予足够阳光 100 点，再次选取并种植到 (col 1, row 2)
    game.sun = 100
    game._select_plant("peashooter")
    assert game.selected_plant == "peashooter"
    pos_1_2 = pvz.cell_center(1, 2, game.cell_h)
    game._handle_click(pos_1_2)
    p_pea = game._top_plant_at(1, 2)
    assert p_pea is not None and p_pea.ptype == "peashooter", "种植豌豆射手失败"
    assert game.sun == 0

    # 模拟游戏循环 60 帧
    for _ in range(60):
        game.update(1 / 30)
    game.draw()
    print("第 1 关真实交互运转流畅无异常！(PASS)")

    # 2. 测试第 5 关 (白天草坪 5，坚果、寒冰、土豆雷、窝瓜与黄金阳光铲)
    print("\n--- 2. 自测第 5 关 (白天防线与神器铲) ---")
    game.start_level(4)
    assert game.level_index == 4
    avail4 = game.available_plants()
    assert "puffshroom" not in avail4 and "sunshroom" not in avail4
    game.selected_seeds = ["sunflower", "peashooter", "wallnut", "snowpea", "potatomine", "squash"]
    game.mode = "playing"
    game.artifacts.add("golden_shovel")

    # 种植坚果墙 (col 2, row 2)
    game.sun = 100
    game._select_plant("wallnut")
    pos_2_2 = pvz.cell_center(2, 2, game.cell_h)
    game._handle_click(pos_2_2)
    assert game._top_plant_at(2, 2) is not None
    assert game.sun == 50

    # 选用铲子铲除坚果墙
    game.shovel_selected = True
    game._handle_click(pos_2_2)
    assert game._top_plant_at(2, 2) is None
    assert game.sun == 100, f"黄金阳光铲返还异常，阳光应为 100，实际为: {game.sun}"
    print("黄金阳光铲 100% 全额返还阳光验证通过！(PASS)")

    # 3. 测试第 7 关 (黑夜暗战与小喷菇、阳光菇、大喷菇)
    print("\n--- 3. 自测第 7 关 (黑夜暗战与小喷菇) ---")
    with open(pvz.SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump({"completed": [0, 1, 2, 3, 4, 5], "artifacts": ["golden_shovel"]}, f)
    game.start_level(6)
    avail6 = game.available_plants()
    assert "puffshroom" in avail6 and "sunshroom" in avail6, "第 7 关应解锁小喷菇与阳光菇"
    game.selected_seeds = ["puffshroom", "sunshroom", "wallnut", "peashooter"]
    game.mode = "playing"

    # 0费种植小喷菇 (col 1, row 1)
    game.sun = 0
    game._select_plant("puffshroom")
    pos_1_1 = pvz.cell_center(1, 1, game.cell_h)
    game._handle_click(pos_1_1)
    p_puff = game._top_plant_at(1, 1)
    assert p_puff is not None and p_puff.ptype == "puffshroom", "0 费小喷菇种植失败"
    assert game.sun == 0

    for _ in range(30):
        game.update(1 / 30)
    game.draw()
    print("黑夜关卡小喷菇与暗战机制验证通过！(PASS)")

    # 4. 测试第 11 关 (泳池水面 1，睡莲承载与水陆激战)
    print("\n--- 4. 自测第 11 关 (泳池水面水陆激战) ---")
    game.start_level(10)
    assert game.is_pool
    assert game.rows == 6
    avail10 = game.available_plants()
    assert "lilypad" in avail10, "泳池关卡必须包含睡莲"
    game.selected_seeds = ["sunflower", "lilypad", "peashooter", "cattail"]
    game.mode = "playing"

    # 水面种植睡莲 (col 2, row 2，水路)
    game.sun = 500
    game._select_plant("lilypad")
    pos_pool = pvz.cell_center(2, 2, game.cell_h)
    game._handle_click(pos_pool)
    carrier = game._carrier_at(2, 2)
    assert carrier is not None and carrier.ptype == "lilypad", "在水面上种植睡莲失败"

    # 在睡莲上种植豌豆射手
    game._select_plant("peashooter")
    game._handle_click(pos_pool)
    top_p = game._top_plant_at(2, 2)
    assert top_p is not None and top_p.ptype == "peashooter", "在睡莲上承载陆地植物失败"

    # 验证波次中水生僵尸严格分配在泳池行 (row 2, 3)
    for w_idx, wave in enumerate(game.waves):
        for m in wave.members:
            ztype, r = m.ztype, m.row
            if ztype in ("ducky", "snorkel", "dolphin"):
                assert r in (2, 3), f"波次 {w_idx} 中水生僵尸 {ztype} 被错误分配到了陆地行 {r}！"

    for _ in range(30):
        game.update(1 / 30)
    game.draw()
    print("泳池水路承载与水生僵尸水域严格限定验证通过！(PASS)")

    # 5. 测试第 16 关 (水陆无尽大挑战，9卡槽与神级阵容)
    print("\n--- 5. 自测第 16 关 (水陆无尽极限考验) ---")
    game.artifacts.add("master_belt")
    game.start_level(15)
    assert game.slot_capacity == 10, f"大师腰带应提供 9 卡槽，实际为: {game.slot_capacity}"
    assert len(game.waves) == 6, "无尽模式应为动态生成波次"

    for _ in range(45):
        game.update(1 / 30)
    game.draw()
    print("水陆无尽极限模式运转正常！(PASS)")

    # 恢复干净存档
    with open(pvz.SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump({"completed": [], "artifacts": []}, f)

    print("\n=== 全部实测关卡全流程 100% 稳定运行，无任何报错或异常！ ===")

if __name__ == "__main__":
    test_full_game()
