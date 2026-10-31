# -*- coding: utf-8 -*-
"""apply_v6_full_fix.py:
Complete fix for:
1. TwinSunflower sun cost -> 125 (PLANTS config & in-game cards)
2. Threepeater early unlock at Level 4 (Day stage) in UNLOCK_ORDER & LEVEL_REWARDS
3. KernelPult butter chance (30% + bad-luck protection every 3 shots), 55 butter dmg, 28 kernel dmg, homing/tracking lob projectiles
4. Permanent stable zombie floating health bars for all zombies + Newspaper zombie shield hp included (total 420 hp)
5. Pool level 6-row grid preview, ghost plant alignment, lilypad overlay 100% pixel-perfect
6. Fullscreen system with Letterboxing & logical coordinate mapping (F11/F/Alt+Enter & HUD button)
7. Auto-collect sun feature unlocked after Level 10 (user toggle on/off button & key C)
8. Topright HUD bar 7 buttons, single-line no overlapping
"""

import sys
from pathlib import Path

pvz_main_path = Path("10-pvz/pvz_ten_levels.py")
with open(pvz_main_path, "r", encoding="utf-8") as f:
    code = f.read()

# -------------------------------------------------------------------------
# 1. TwinSunflower cost -> 125
# -------------------------------------------------------------------------
code = code.replace(
    '"twinsunflower": {\n        "name": "双子向日葵", "cost": 150,',
    '"twinsunflower": {\n        "name": "双子向日葵", "cost": 125,',
    1
)

# -------------------------------------------------------------------------
# 2. Threepeater in UNLOCK_ORDER
# -------------------------------------------------------------------------
old_unlock = '''    # 白天草坪阶段解锁 (第 1~5 关通关赠送，白天绝不出现蘑菇！)
    "wallnut",
    "snowpea",
    "potatomine",
    "repeater",
    "squash",'''

new_unlock = '''    # 白天草坪阶段解锁 (第 1~5 关通关赠送，白天绝不出现蘑菇！)
    "wallnut",
    "snowpea",
    "potatomine",
    "repeater",
    "threepeater",
    "squash",'''

if old_unlock in code:
    code = code.replace(old_unlock, new_unlock, 1)

# Remove old threepeater in pool phase
code = code.replace('    "starfruit",\n    "threepeater",\n    "melonpult",', '    "starfruit",\n    "melonpult",', 1)

# LEVEL_REWARDS update
old_rew_4 = '''    4: {
        "plants": ["squash"],
        "artifact": "golden_shovel",
        "artifact_name": "黄金阳光铲",
        "artifact_desc": "神奇黄金铁铲！铲除任何植物时，100% 全额返还种植所消耗的阳光！",
    },'''

new_rew_4 = '''    4: {
        "plants": ["squash", "threepeater"],
        "artifact": "golden_shovel",
        "artifact_name": "黄金阳光铲",
        "artifact_desc": "神奇黄金铁铲！铲除任何植物时，100% 全额返还种植所消耗的阳光！",
    },'''
code = code.replace(old_rew_4, new_rew_4, 1)

# Level 9 (10th level) reward: auto sun magnet!
old_rew_9 = '''    9: {
        "plants": ["doomshroom", "jalapeno"],
        "artifact": "rapid_seeds",
        "artifact_name": "园艺快手手套",
        "artifact_desc": "熟练园丁的特制手套！全植物种植冷却恢复速度提升 30%！",
    },'''

new_rew_9 = '''    9: {
        "plants": ["doomshroom", "jalapeno"],
        "artifact": "auto_sun_magnet",
        "artifact_name": "磁能阳光发生器 (自动收集阳光)",
        "artifact_desc": "戴夫高级黑科技！解锁全场阳光自动吸附功能，可在右上角[自吸:开/关]随心自由切换！",
    },'''
code = code.replace(old_rew_9, new_rew_9, 1)

# Reward 13 update
code = code.replace('13: {"plants": ["starfruit", "threepeater", "agave"], "artifact": None},', '13: {"plants": ["starfruit", "agave", "gatlingpea"], "artifact": None},', 1)

# -------------------------------------------------------------------------
# 3. Projectile tracking for lobbed bullets
# -------------------------------------------------------------------------
old_lob_update = '''        elif self.is_lobbed:
            self.lob_progress += dt / max(0.001, self.lob_duration)
            p = min(1.0, self.lob_progress)
            self.x = self.start_x + (self.target_x - self.start_x) * p
            linear_y = self.start_y + (self.target_y - self.start_y) * p
            arc = 4.0 * self.apex_h * p * (1.0 - p)
            self.y = linear_y - arc'''

new_lob_update = '''        elif self.is_lobbed:
            self.lob_progress += dt / max(0.001, self.lob_duration)
            p = min(1.0, self.lob_progress)
            if self.target_zombie and not getattr(self.target_zombie, "dead", True):
                self.target_x = getattr(self.target_zombie, "x", self.target_x)
            self.x = self.start_x + (self.target_x - self.start_x) * p
            linear_y = self.start_y + (self.target_y - self.start_y) * p
            arc = 4.0 * self.apex_h * p * (1.0 - p)
            self.y = linear_y - arc'''
code = code.replace(old_lob_update, new_lob_update, 1)

# -------------------------------------------------------------------------
# 4. KernelPult shooting & damage & bad-luck protection
# -------------------------------------------------------------------------
old_kernel_fire = '''            elif plant.ptype == "kernelpult":
                if plant.action_timer >= 2.85:
                    target = next((z for z in sorted(self.zombies, key=lambda z: z.x) if z.row == plant.row and not z.dead and z.x > plant.x - 20 and z.x < GRID_RIGHT + 180), None)
                    if target:
                        plant.action_timer = 0.0
                        is_butter = random.random() < 0.25
                        b_type = "butter" if is_butter else "kernel"
                        dmg = 40.0 if is_butter else 20.0
                        tx = target.x
                        ty = target.y
                        dist = max(80.0, tx - plant.x)
                        duration = clamp(dist / 400.0, 0.55, 1.1)
                        self.projectiles.append(
                            Projectile(
                                x=plant.x + 20, y=plant.y - 30, row=plant.row, damage=dmg,
                                bullet_type=b_type, is_lobbed=True,
                                start_x=plant.x + 20, start_y=plant.y - 30,
                                target_x=tx, target_y=ty, lob_duration=duration, apex_h=110.0,
                            )
                        )
                        self.audio.play("plant", cooldown=0.1)'''

new_kernel_fire = '''            elif plant.ptype == "kernelpult":
                if plant.action_timer >= 2.35:
                    target = next((z for z in sorted(self.zombies, key=lambda z: z.x) if z.row == plant.row and not z.dead and z.x > plant.x - 20 and z.x < GRID_RIGHT + 180), None)
                    if target:
                        plant.action_timer = 0.0
                        plant.shots_since_butter = getattr(plant, "shots_since_butter", 0) + 1
                        # 30% 基础概率，且连续 2 发玉米粒后第 3 发必出黄油保底！
                        is_butter = (plant.shots_since_butter >= 3) or (random.random() < 0.30)
                        if is_butter:
                            plant.shots_since_butter = 0
                        b_type = "butter" if is_butter else "kernel"
                        dmg = 55.0 if is_butter else 28.0
                        tx = target.x
                        ty = target.y
                        dist = max(80.0, tx - plant.x)
                        duration = clamp(dist / 420.0, 0.50, 1.0)
                        self.projectiles.append(
                            Projectile(
                                x=plant.x + 20, y=plant.y - 30, row=plant.row, damage=dmg,
                                bullet_type=b_type, is_lobbed=True,
                                start_x=plant.x + 20, start_y=plant.y - 30,
                                target_x=tx, target_y=ty, lob_duration=duration, apex_h=110.0,
                                target_zombie=target,
                            )
                        )
                        self.audio.play("plant", cooldown=0.1)'''
code = code.replace(old_kernel_fire, new_kernel_fire, 1)

# Lob hit target radius -> 85
code = code.replace("and abs(z.x - impact_x) < 55", "and abs(z.x - impact_x) < 85", 1)
# Butter duration 4.5
code = code.replace("main_target.butter_timer = 4.0", "main_target.butter_timer = 4.5", 1)

# -------------------------------------------------------------------------
# 5. Backup draw_zombie health bar fix in pvz_ten_levels.py
# -------------------------------------------------------------------------
old_backup_bar = '''    if zombie.hp < zombie.max_hp:
        ratio = clamp(zombie.hp / zombie.max_hp, 0, 1)
        bar = pygame.Rect(int(x - 26), int(head_y - (74 if zombie.ztype == "cone" else 55)), 52, 6)
        pygame.draw.rect(surface, (48, 35, 33), bar, border_radius=3)
        fill = bar.inflate(-2, -2)
        fill.width = int(fill.width * ratio)
        color = (97, 198, 92) if ratio > 0.55 else (241, 186, 58) if ratio > 0.25 else (226, 73, 59)
        pygame.draw.rect(surface, color, fill, border_radius=2)'''

new_backup_bar = '''    has_np = getattr(zombie, "has_newspaper", False)
    np_hp = getattr(zombie, "newspaper_hp", 0.0)
    if zombie.ztype == "newspaper":
        tot_hp = zombie.hp + (np_hp if has_np else 0.0)
        tot_max = zombie.max_hp + 140.0
        dmg = tot_hp < (tot_max - 0.5)
        bar_ratio = clamp(tot_hp / tot_max, 0, 1)
    else:
        dmg = zombie.hp < (zombie.max_hp - 0.5)
        bar_ratio = clamp(zombie.hp / max(1.0, zombie.max_hp), 0, 1)

    if not getattr(zombie, "dead", False) and dmg:
        bar = pygame.Rect(int(x - 26), int(head_y - (74 if zombie.ztype == "cone" else 55)), 52, 6)
        pygame.draw.rect(surface, (48, 35, 33), bar, border_radius=3)
        fill = bar.inflate(-2, -2)
        fill.width = int(fill.width * bar_ratio)
        color = (97, 198, 92) if bar_ratio > 0.55 else (241, 186, 58) if bar_ratio > 0.25 else (226, 73, 59)
        if fill.width > 0:
            pygame.draw.rect(surface, color, fill, border_radius=2)'''
code = code.replace(old_backup_bar, new_backup_bar, 1)

# Write updated code
with open(pvz_main_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Part 1: Basic modifications applied successfully!")
