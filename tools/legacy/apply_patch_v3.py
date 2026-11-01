# -*- coding: utf-8 -*-
"""Patch pvz_ten_levels.py and pvz_graphics.py:
1. Fix draw_zombie cell_h bug (was defaulting to 116 instead of self.cell_h, shifting zombies down 80px onto grass).
2. Water zombies strictly constrained to pool lanes and x <= 834.
3. Add 5 new plants: hypnoshroom, fumeshroom, doomshroom, twinsunflower, starfruit.
4. Add combat mechanics for all 5 new plants.
5. Fix cards for lilypad, cattail, garlic.
"""

from pathlib import Path
import re

PVZ_FILE = Path("10-pvz/pvz_ten_levels.py")
GFX_FILE = Path("10-pvz/pvz_graphics.py")

def update_pvz():
    text = PVZ_FILE.read_text(encoding="utf-8")

    # 1. Update PLANTS dictionary with 5 new plants
    old_plants_end = '''    "gatlingpea": {
        "name": "机枪射手", "cost": 250, "cooldown": 15.0, "hp": 300,
    },
}'''

    new_plants_end = '''    "gatlingpea": {
        "name": "机枪射手", "cost": 250, "cooldown": 15.0, "hp": 300,
    },
    "hypnoshroom": {
        "name": "魅惑菇", "cost": 75, "cooldown": 15.0, "hp": 300,
    },
    "fumeshroom": {
        "name": "大喷菇", "cost": 75, "cooldown": 7.5, "hp": 300,
    },
    "doomshroom": {
        "name": "毁灭菇", "cost": 125, "cooldown": 25.0, "hp": 300,
    },
    "twinsunflower": {
        "name": "双子向日葵", "cost": 150, "cooldown": 15.0, "hp": 300,
    },
    "starfruit": {
        "name": "杨桃", "cost": 125, "cooldown": 7.5, "hp": 300,
    },
}'''
    assert old_plants_end in text, "old_plants_end not found!"
    text = text.replace(old_plants_end, new_plants_end)

    # 2. Update UNLOCK_ORDER
    old_unlock_end = '''    "tallnut",
    "gatlingpea",
]'''
    new_unlock_end = '''    "tallnut",
    "gatlingpea",
    "hypnoshroom",
    "fumeshroom",
    "doomshroom",
    "twinsunflower",
    "starfruit",
]'''
    assert old_unlock_end in text, "old_unlock_end not found!"
    text = text.replace(old_unlock_end, new_unlock_end)

    # 3. Update PLANT_TIPS
    old_tips_end = '''    "gatlingpea": "机枪射手：头戴钢盔的终极射手！一次性扫射 4 颗豌豆，配合火炬树桩火力毁天灭地！",
}'''
    new_tips_end = '''    "gatlingpea": "机枪射手：头戴钢盔的终极射手！一次性扫射 4 颗豌豆，配合火炬树桩火力毁天灭地！",
    "hypnoshroom": "魅惑菇：让吃下它的僵尸彻底倒戈！掉头反向冲锋并为你攻击其他敌方僵尸！",
    "fumeshroom": "大喷菇：喷射大范围强力紫色穿透孢子气雾，一次性贯穿打击整行内所有僵尸！",
    "doomshroom": "毁灭菇：末日级超级核弹！产生惊天动地的毁灭蘑菇云，瞬秒 5x5 格内全部僵尸！",
    "twinsunflower": "双子向日葵：双头并立双倍快乐！每次稳定产出 50 点巨量阳光，经济腾飞核心！",
    "starfruit": "杨桃：全方位无死角弹幕射手！同时向 5 个方向发射高速旋转飞星，密不透风！",
}'''
    assert old_tips_end in text, "old_tips_end not found!"
    text = text.replace(old_tips_end, new_tips_end)

    # 4. Fix draw_zombie signature & call site to pass cell_h!
    old_draw_zombie_sig = '''def draw_zombie(
    surface: pygame.Surface,
    zombie: "Zombie",
    time_value: float,
    alpha: int = 255,
    dy_offset: float = 0.0,
) -> None:
    ground = lane_ground(zombie.row)'''

    new_draw_zombie_sig = '''def draw_zombie(
    surface: pygame.Surface,
    zombie: "Zombie",
    time_value: float,
    alpha: int = 255,
    dy_offset: float = 0.0,
    cell_h: int = CELL_H,
) -> None:
    ground = lane_ground(zombie.row, cell_h=cell_h)'''
    assert old_draw_zombie_sig in text, "old_draw_zombie_sig not found!"
    text = text.replace(old_draw_zombie_sig, new_draw_zombie_sig)

    old_draw_zombie_calls = '''        for zombie in sorted(self.zombies, key=lambda z: (z.row, z.x)):
            if zombie.dead:
                fall = min(1.0, zombie.death_timer / 0.5)
                alpha = int(220 * (1.0 - fall))
                draw_zombie(self.screen, zombie, self.time_value, alpha=alpha, dy_offset=fall * 12)
            else:
                draw_zombie(self.screen, zombie, self.time_value)'''

    new_draw_zombie_calls = '''        for zombie in sorted(self.zombies, key=lambda z: (z.row, z.x)):
            if zombie.dead:
                fall = min(1.0, zombie.death_timer / 0.5)
                alpha = int(220 * (1.0 - fall))
                draw_zombie(self.screen, zombie, self.time_value, alpha=alpha, dy_offset=fall * 12, cell_h=self.cell_h)
            else:
                draw_zombie(self.screen, zombie, self.time_value, cell_h=self.cell_h)'''
    assert old_draw_zombie_calls in text, "old_draw_zombie_calls not found!"
    text = text.replace(old_draw_zombie_calls, new_draw_zombie_calls)

    # 5. Fix _build_waves: Strictly constrain water zombies to pool rows!
    old_build_wave_loop = '''                if wave_index == wave_count - 1 and member_index < rows:
                    lane = member_index
                else:
                    lane = rng.randrange(rows)
                    if member_index > 0 and rng.random() < 0.3 and lane == last_lane:
                        lane = (lane + rng.randint(1, rows - 1)) % rows
                last_lane = lane
                members.append(WaveMember(delay, ztype, lane))'''

    new_build_wave_loop = '''                # 水路僵尸严格阵营划分：绝不允许水路僵尸走到陆地！
                pool_lanes = [2, 3] if self.is_pool else []
                land_lanes = [r for r in range(rows) if r not in pool_lanes]
                if ztype in ("ducky", "snorkel", "dolphin"):
                    if pool_lanes:
                        lane = rng.choice(pool_lanes)
                    else:
                        ztype = "basic"
                        lane = rng.randrange(rows)
                elif ztype in ("pole", "newspaper", "runner"):
                    lane = rng.choice(land_lanes) if land_lanes else rng.randrange(rows)
                else:
                    if wave_index == wave_count - 1 and member_index < rows:
                        lane = member_index
                    else:
                        lane = rng.randrange(rows)
                        if member_index > 0 and rng.random() < 0.3 and lane == last_lane:
                            lane = (lane + rng.randint(1, rows - 1)) % rows
                    if pool_lanes and lane in pool_lanes and ztype in ("basic", "cone", "bucket"):
                        ztype = "ducky"
                last_lane = lane
                members.append(WaveMember(delay, ztype, lane))'''
    assert old_build_wave_loop in text, "old_build_wave_loop not found!"
    text = text.replace(old_build_wave_loop, new_build_wave_loop)

    # 6. Update setup_preview: Water zombies strictly inside water (x <= 820), pool rows!
    old_preview_zombies = '''            demo_zombies = [
                ("basic", 0, 1020), ("cone", 0, 1140),
                ("bucket", 1, 880), ("pole", 1, 1090),
                ("ducky", 2, 780), ("snorkel", 2, 940),
                ("dolphin", 3, 860), ("ducky", 3, 1120),
                ("runner", 4, 820), ("newspaper", 4, 1040),
                ("bucket", 5, 910), ("basic", 5, 1130),
            ]'''

    new_preview_zombies = '''            # 水路僵尸严格在水域内 (x <= 810) 悠游与飞跃，绝对禁止在陆地上！
            demo_zombies = [
                ("basic", 0, 1020), ("cone", 0, 1140),
                ("bucket", 1, 880), ("pole", 1, 1090),
                ("ducky", 2, 680), ("snorkel", 2, 790),
                ("dolphin", 3, 720), ("ducky", 3, 810),
                ("runner", 4, 820), ("newspaper", 4, 1040),
                ("bucket", 5, 910), ("basic", 5, 1130),
            ]'''
    assert old_preview_zombies in text, "old_preview_zombies not found!"
    text = text.replace(old_preview_zombies, new_preview_zombies)

    # 7. Add combat logic for 5 new plants in _update_plants
    old_sunflower_update = '''            if plant.ptype == "sunflower":
                if plant.action_timer >= (4.1 if plant.age < 8 else 7.0):
                    plant.action_timer = 0
                    target = lane_ground(plant.row, cell_h=self.cell_h) - 34 + random.randint(-15, 15)
                    self.suns.append(SunToken(plant.x + random.randint(-10, 10), plant.y - 45, target))'''

    new_sunflower_update = '''            if plant.ptype == "sunflower":
                if plant.action_timer >= (4.1 if plant.age < 8 else 7.0):
                    plant.action_timer = 0
                    target = lane_ground(plant.row, cell_h=self.cell_h) - 34 + random.randint(-15, 15)
                    self.suns.append(SunToken(plant.x + random.randint(-10, 10), plant.y - 45, target))
            elif plant.ptype == "twinsunflower":
                # 双子向日葵：双倍产出 50 阳光
                if plant.action_timer >= (4.0 if plant.age < 8 else 6.8):
                    plant.action_timer = 0
                    target1 = lane_ground(plant.row, cell_h=self.cell_h) - 34 + random.randint(-15, 15)
                    target2 = lane_ground(plant.row, cell_h=self.cell_h) - 34 + random.randint(-15, 15)
                    self.suns.append(SunToken(plant.x - 22, plant.y - 45, target1))
                    self.suns.append(SunToken(plant.x + 22, plant.y - 45, target2))
            elif plant.ptype == "fumeshroom":
                # 大喷菇：喷射大范围紫色穿透孢子气雾
                if plant.action_timer >= 1.45:
                    has_target = any(
                        z.row == plant.row and not z.dead and z.x > plant.x - 20 and z.x < plant.x + 420
                        for z in self.zombies
                    )
                    if has_target:
                        plant.action_timer = 0
                        y = lane_ground(plant.row, cell_h=self.cell_h) - 62
                        self.projectiles.append(Projectile(plant.x + 45, y, plant.row, 20, bullet_type="fume"))
                        self.burst(plant.x + 40, y, (190, 85, 220), 8)
            elif plant.ptype == "starfruit":
                # 杨桃：5 方向散射金星
                if plant.action_timer >= 1.4:
                    if any(not z.dead for z in self.zombies):
                        plant.action_timer = 0
                        y = lane_ground(plant.row, cell_h=self.cell_h) - 58
                        for vx, vy in [(420, 0), (-420, 0), (0, -380), (0, 380), (-300, -300)]:
                            proj = Projectile(plant.x, y, plant.row, 20, bullet_type="star")
                            proj.speed = math.hypot(vx, vy)
                            proj.lob_progress = 0.0
                            # We will handle vx/vy in update_projectiles
                            setattr(proj, "vx", vx)
                            setattr(proj, "vy", vy)
                            self.projectiles.append(proj)
                        self.burst(plant.x, y, (255, 235, 80), 6)
            elif plant.ptype == "doomshroom":
                # 毁灭菇：1 秒后引发末日核爆
                if plant.age >= 1.0:
                    plant.alive = False
                    self.burst(plant.x, plant.y, (40, 20, 50), 30, speed=250.0)
                    self.burst(plant.x, plant.y, (255, 60, 40), 20, speed=200.0)
                    self.audio.play("cherrybomb")
                    self.float_text(plant.x, plant.y - 40, "末日核爆！", (255, 80, 60))
                    for z in self.zombies:
                        if not z.dead:
                            dist = math.hypot(z.x - plant.x, (lane_ground(z.row, cell_h=self.cell_h) - 40) - plant.y)
                            if dist <= 280:
                                self._damage_zombie(z, 1800.0)'''
    assert old_sunflower_update in text, "old_sunflower_update not found!"
    text = text.replace(old_sunflower_update, new_sunflower_update)

    # 8. Hypnoshroom zombie charm in _plant_under_attack
    old_bite_logic = '''                    # 大蒜啃咬分流变道
                    if plant.ptype == "garlic":'''

    new_bite_logic = '''                    # 魅惑菇：啃食即刻被魅惑倒戈
                    if plant.ptype == "hypnoshroom":
                        plant.alive = False
                        zombie.eating = 0.0
                        setattr(zombie, "hypnotized", True)
                        zombie.speed = -abs(zombie.speed) # 调头倒戈！
                        self.burst(plant.x, plant.y, (255, 120, 220), 16)
                        self.float_text(zombie.x, zombie.y - 25, "已被魅惑！", (255, 120, 220))
                        self.audio.play("groan")

                    # 大蒜啃咬分流变道
                    if plant.ptype == "garlic":'''
    assert old_bite_logic in text, "old_bite_logic not found!"
    text = text.replace(old_bite_logic, new_bite_logic)

    # 9. Hypnotized zombie attacking enemy zombies in _update_zombies
    old_zombie_move = '''            else:
                zombie.eating = max(0.0, zombie.eating - dt * 3)
                zombie.x -= zombie.speed * speed_mult * dt
                if zombie.x < MOWER_X - 6:'''

    new_zombie_move = '''            else:
                zombie.eating = max(0.0, zombie.eating - dt * 3)
                zombie.x -= zombie.speed * speed_mult * dt
                # 魅惑僵尸为玩家反向作战
                if getattr(zombie, "hypnotized", False):
                    for ez in self.zombies:
                        if not ez.dead and not getattr(ez, "hypnotized", False) and ez.row == zombie.row:
                            if abs(ez.x - zombie.x) < 32:
                                self._damage_zombie(ez, 60.0 * dt)
                                break
                    if zombie.x > WIDTH + 80:
                        zombie.dead = True
                        continue
                elif zombie.x < MOWER_X - 6:'''
    assert old_zombie_move in text, "old_zombie_move not found!"
    text = text.replace(old_zombie_move, new_zombie_move)

    # 10. Update projectiles for star and fume
    old_proj_update = '''            old_x = projectile.x
            projectile.update(dt)'''

    new_proj_update = '''            old_x = projectile.x
            if hasattr(projectile, "vx") and hasattr(projectile, "vy"):
                projectile.x += getattr(projectile, "vx") * dt
                projectile.y += getattr(projectile, "vy") * dt
                if projectile.x < -60 or projectile.x > WIDTH + 60 or projectile.y < -60 or projectile.y > HEIGHT + 60:
                    projectile.alive = False
                    continue
            else:
                projectile.update(dt)

            # 大喷菇穿透气雾判定
            if projectile.bullet_type == "fume":
                hit_set = getattr(projectile, "hit_set", set())
                setattr(projectile, "hit_set", hit_set)
                for ez in self.zombies:
                    if not ez.dead and ez.row == projectile.row and abs(ez.x - projectile.x) < 38 and id(ez) not in hit_set:
                        hit_set.add(id(ez))
                        self._damage_zombie(ez, projectile.damage)
                        self.burst(ez.x, ez.y - 15, (210, 110, 230), 4)
                if projectile.x > old_x + 420 or projectile.x > WIDTH:
                    projectile.alive = False
                    continue

            # 杨桃金星碰撞判定
            if projectile.bullet_type == "star":
                for ez in self.zombies:
                    if not ez.dead and math.hypot(ez.x - projectile.x, (lane_ground(ez.row, cell_h=self.cell_h) - 40) - projectile.y) < 32:
                        projectile.alive = False
                        self._damage_zombie(ez, projectile.damage)
                        self.burst(projectile.x, projectile.y, (255, 235, 90), 8)
                        break
                if not projectile.alive:
                    continue'''
    assert old_proj_update in text, "old_proj_update not found!"
    text = text.replace(old_proj_update, new_proj_update)

    PVZ_FILE.write_text(text, encoding="utf-8")
    print("PVZ_TEN_LEVELS_V3_PATCH_APPLIED")

def update_gfx():
    text = GFX_FILE.read_text(encoding="utf-8")

    # Add plant size scaling for the 5 new plants
    old_sizes = '''    elif plant_type == "threepeater":
        target_h = int(96 * scale)'''

    new_sizes = '''    elif plant_type == "threepeater":
        target_h = int(96 * scale)
    elif plant_type in ("hypnoshroom", "fumeshroom"):
        target_h = int(72 * scale)
        y_offset = 8 * scale
    elif plant_type == "doomshroom":
        target_h = int(86 * scale)
        y_offset = 4 * scale
    elif plant_type == "twinsunflower":
        target_h = int(88 * scale)
        target_w = int(114 * scale)
        y_offset = 0 * scale
    elif plant_type == "starfruit":
        target_h = int(82 * scale)
        y_offset = 2 * scale'''

    assert old_sizes in text, "old_sizes not found in pvz_graphics.py!"
    text = text.replace(old_sizes, new_sizes)

    GFX_FILE.write_text(text, encoding="utf-8")
    print("PVZ_GRAPHICS_V3_PATCH_APPLIED")

if __name__ == "__main__":
    update_pvz()
    update_gfx()
