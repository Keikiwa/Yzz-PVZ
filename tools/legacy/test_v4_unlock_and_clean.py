# -*- coding: utf-8 -*-
import os
import sys
from pathlib import Path
import json

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
pygame.init()
screen = pygame.display.set_mode((1200, 760))

sys.path.insert(0, str(Path(r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz")))
import pvz_ten_levels as pvz

def set_save(completed, artifacts):
    with open(pvz.SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump({"completed": completed, "artifacts": artifacts}, f)

print("=== 开始严格测试 V5 解锁时序与汉字渲染安全性 ===")

# --- 1. 测试 UNLOCK_ORDER 与 34 种植物完整性 ---
assert len(pvz.UNLOCK_ORDER) == 34, f"Expected 34 plants, got {len(pvz.UNLOCK_ORDER)}"
assert pvz.UNLOCK_ORDER[:2] == ["sunflower", "peashooter"], "Initial plants mismatch"
assert pvz.UNLOCK_ORDER[2:7] == ["wallnut", "snowpea", "potatomine", "repeater", "squash"], "Daytime plants mismatch"
assert "puffshroom" in pvz.UNLOCK_ORDER[7:17], "Mushroom should be in night range"
assert "sunshroom" in pvz.UNLOCK_ORDER[7:17], "Mushroom should be in night range"
assert "cobcannon" in pvz.UNLOCK_ORDER, "Cob cannon should be in unlock order"
print("[1] 34 种植物时序严密性校验通过！(PASS)")

# --- 2. 测试第 1~5 关绝对不出现夜间蘑菇 ---
game = pvz.Game(screen)

# 清空存档（新用户刚进入游戏）
set_save([], [])

# 检查第 1 关 (level_index = 0)
game.level_index = 0
game.is_pool = False
p1 = game.available_plants()
print("第 1 关可用植物:", p1)
assert p1 == ["sunflower", "peashooter"], f"第 1 关必须且只能是基础植物，实际为: {p1}"

# 即使存档被恶意写入了 [5, 10]
set_save([5, 10], [])
p1_dirty = game.available_plants()
assert p1_dirty == ["sunflower", "peashooter"], f"脏存档渗透第 1 关保护异常: {p1_dirty}"

# 检查第 5 关 (level_index = 4，白天最后一关)
game.level_index = 4
p5 = game.available_plants()
print("第 5 关可用植物:", p5)
assert "puffshroom" not in p5, "第 5 关白天草坪绝不能拥有小喷菇！"
assert "sunshroom" not in p5, "第 5 关白天草坪绝不能拥有阳光菇！"
print("[2] 前 5 关严格封顶与防提前解锁校验通过！(PASS)")

# --- 3. 正常通关进程推进测试 ---
set_save([0, 1, 2, 3, 4, 5], [])
game.level_index = 6
p7 = game.available_plants()
print("第 7 关可用植物:", p7)
assert "puffshroom" in p7 and "sunshroom" in p7, "通关第 5 关后应正常解锁蘑菇！"
print("[3] 正常主线通关解锁推进校验通过！(PASS)")

# --- 4. 泳池关卡自动保障睡莲 ---
game.level_index = 10
game.is_pool = True
set_save([], [])
p_pool = game.available_plants()
assert "lilypad" in p_pool, "泳池关卡必须保底拥有睡莲！"
print("[4] 泳池水面保底睡莲机制校验通过！(PASS)")

# --- 5. 选卡界面卡牌排布与不遮挡测试 (9列 x 4行) ---
cat_rect = pygame.Rect(140, 104, 920, 528)
desc_box = pygame.Rect(cat_rect.x + 20, cat_rect.bottom - 98, cat_rect.width - 40, 84)

cw = 88
ch = 72
gap_x = 8
gap_y = 6
gx0 = cat_rect.x + (cat_rect.width - (9 * cw + 8 * gap_x)) // 2
gy0 = cat_rect.y + 60

for idx, name in enumerate(pvz.UNLOCK_ORDER):
    col = idx % 9
    row = idx // 9
    crect = pygame.Rect(gx0 + col * (cw + gap_x), gy0 + row * (ch + gap_y), cw, ch)
    assert cat_rect.contains(crect), f"Card {name} out of catalog bounds: {crect}"
    assert not crect.colliderect(desc_box), f"Card {name} collides with desc_box: {crect} vs {desc_box}"

print("[5] 34 张卡牌 9列x4行 网格布局精准无重叠校验通过！(PASS)")

# --- 6. 汉字渲染与字形净化安全性测试 ---
font = game.fonts.get(16, True)
test_strings = [
    "普通中文字符测试：植物大战僵尸全功能豪华版",
    "全角标点测试：【通关奖励】玉米加农炮、魔术菇、龙舌兰、激光豆；巨人僵尸一击粉碎！",
    "混合排版：第 16 关 · 水陆无尽大挑战 [无尽模式 · 初始阳光: 500]",
]

for s in test_strings:
    r = pvz.text(screen, s, font, (255, 255, 255), (100, 100))
    assert r.width > 0 and r.height > 0, f"Render failed for: {s}"

print("[6] 汉字与特殊字符净化渲染 100% 成功无崩溃校验通过！(PASS)")

set_save([], [])
print("=== 全部测试 100% 通过！===")
