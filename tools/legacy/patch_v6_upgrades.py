# -*- coding: utf-8 -*-
"""Comprehensive Patch V6:
1. TwinSunflower sun cost -> 125
2. KernelPult butter chance 30% with guarantee, 55 dmg, 28 kernel dmg, homing/tracking lob projectiles
3. Newspaper zombie shield health bar & permanent stable floating health bar for all zombies
4. Pool level grid preview, ghost plant alignment & lilypad overlay planting 100% pixel-perfect
5. Fullscreen system with Letterboxing & logical coordinate mapping (F11/F/Alt+Enter & HUD button)
6. Threepeater early unlock at Level 4 (Day stage)
7. Topright HUD bar: 6 buttons ([1x速], [暂停], [铲子], [全屏], [音效], [跳关]), single-line no overlapping
"""

from pathlib import Path
import re

pvz_main_path = Path("10-pvz/pvz_ten_levels.py")
pvz_gfx_path = Path("10-pvz/pvz_graphics.py")

# =========================================================================
# Step 1: Update pvz_graphics.py (Health bar & Butter face)
# =========================================================================
with open(pvz_gfx_path, "r", encoding="utf-8") as f:
    gfx_code = f.read()

old_gfx_tail = """    # 黄油糊脸特写 (被玉米黄油击中时)
    butter_t = getattr(zombie, "butter_timer", 0.0)
    if butter_t > 0:
        butter_surf = _ITEM_SURFACES.get("butter")
        if butter_surf:
            b_scaled = _get_scaled(butter_surf, 32, 22)
            surface.blit(b_scaled, (int(zombie.x - 16), int(draw_y - 6)))

    # 血条绘制 (仅在未死亡且受伤时)
    if alpha >= 200 and zombie.hp < zombie.max_hp:
        ratio = max(0.0, min(1.0, zombie.hp / zombie.max_hp))
        bar = pygame.Rect(int(zombie.x - 24), int(draw_y - 8), 48, 6)
        pygame.draw.rect(surface, (45, 30, 30), bar, border_radius=3)
        fill = bar.inflate(-2, -2)
        fill.width = int(fill.width * ratio)
        col = (97, 198, 92) if ratio > 0.55 else (241, 186, 58) if ratio > 0.25 else (226, 73, 59)
        pygame.draw.rect(surface, col, fill, border_radius=2)

    return True"""

new_gfx_tail = """    # 黄油糊脸特写 (被玉米黄油击中时，鲜黄醒目)
    butter_t = getattr(zombie, "butter_timer", 0.0)
    if butter_t > 0:
        butter_surf = _ITEM_SURFACES.get("butter")
        if butter_surf:
            b_scaled = _get_scaled(butter_surf, 38, 26)
            surface.blit(b_scaled, (int(zombie.x - 19), int(ground_y - 82 + vault_y)))

    # 血条绘制 (读报僵尸护盾及各僵尸受伤时稳定常显，高度固定不随动作跳跃)
    has_np = getattr(zombie, "has_newspaper", False)
    np_hp = getattr(zombie, "newspaper_hp", 0.0)
    if ztype == "newspaper":
        total_hp = zombie.hp + (np_hp if has_np else 0.0)
        total_max = zombie.max_hp + 140.0
        damaged = total_hp < (total_max - 0.5)
        ratio = max(0.0, min(1.0, total_hp / total_max))
    else:
        damaged = zombie.hp < (zombie.max_hp - 0.5)
        ratio = max(0.0, min(1.0, zombie.hp / max(1.0, zombie.max_hp)))

    if not getattr(zombie, "dead", False) and damaged and alpha >= 100:
        if ztype == "gargantuar":
            bar_y = int(ground_y - 142 + vault_y)
            bar_w = 64
        elif ztype == "imp":
            bar_y = int(ground_y - 48)
            bar_w = 34
        elif ztype == "balloon" and getattr(zombie, "flying", True):
            bar_y = int(ground_y - 118 + balloon_y)
            bar_w = 48
        else:
            bar_y = int(ground_y - 94 + vault_y)
            bar_w = 48

        bar = pygame.Rect(int(zombie.x - bar_w // 2), bar_y, bar_w, 6)
        pygame.draw.rect(surface, (45, 30, 30), bar, border_radius=3)
        fill = bar.inflate(-2, -2)
        fill.width = int(fill.width * ratio)
        col = (97, 198, 92) if ratio > 0.55 else (241, 186, 58) if ratio > 0.25 else (226, 73, 59)
        if fill.width > 0:
            pygame.draw.rect(surface, col, fill, border_radius=2)

    return True"""

old_gfx_tail_crlf = old_gfx_tail.replace("\n", "\r\n")
if old_gfx_tail in gfx_code:
    gfx_code = gfx_code.replace(old_gfx_tail, new_gfx_tail, 1)
    print("Updated pvz_graphics.py (LF)")
elif old_gfx_tail_crlf in gfx_code:
    gfx_code = gfx_code.replace(old_gfx_tail_crlf, new_gfx_tail.replace("\n", "\r\n"), 1)
    print("Updated pvz_graphics.py (CRLF)")
else:
    print("Warning: old_gfx_tail not found directly in pvz_graphics.py")

with open(pvz_gfx_path, "w", encoding="utf-8") as f:
    f.write(gfx_code)

print("Step 1 Complete: Graphics updated.")
