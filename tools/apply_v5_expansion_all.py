# -*- coding: utf-8 -*-
"""Full expansion patch for PVZ:
- Add 4 new legendary plants: cobcannon, magicshroom, agave, laserbean (Total 34 plants)
- Add 5 new elite zombies: gargantuar, imp, balloon, jackbox, digger (Total 15 zombies)
- Full combat logic & AI implementation
- UI 9x4 catalog layout & wave distributions
"""

import re
from pathlib import Path

pvz_path = Path(r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\pvz_ten_levels.py")
code = pvz_path.read_text(encoding="utf-8")

# 1. 扩充 PLANTS 配置字典
old_plants_end = """    "twinsunflower": {"name": "双子向日葵", "cost": 150, "hp": 300, "cooldown": 15.0, "type": "economy"},
    "starfruit": {"name": "杨桃", "cost": 125, "hp": 300, "cooldown": 7.5, "type": "star"},
}"""

new_plants_end = """    "twinsunflower": {"name": "双子向日葵", "cost": 150, "hp": 300, "cooldown": 15.0, "type": "economy"},
    "starfruit": {"name": "杨桃", "cost": 125, "hp": 300, "cooldown": 7.5, "type": "star"},
    "cobcannon": {"name": "玉米加农炮", "cost": 500, "hp": 1200, "cooldown": 30.0, "type": "cannon"},
    "magicshroom": {"name": "魔术菇", "cost": 175, "hp": 300, "cooldown": 10.0, "type": "magic"},
    "agave": {"name": "龙舌兰", "cost": 150, "hp": 600, "cooldown": 10.0, "type": "melee"},
    "laserbean": {"name": "激光豆", "cost": 200, "hp": 300, "cooldown": 10.0, "type": "laser"},
}"""

if old_plants_end in code:
    code = code.replace(old_plants_end, new_plants_end)
    print("PLANTS expanded!")

# 2. 扩充 ZOMBIES 配置字典
old_zombies_end = """    "ducky": {"name": "救生圈鸭鸭", "hp": 180, "speed": 17.0, "damage": 28},
    "snorkel": {"name": "潜水僵尸", "hp": 210, "speed": 19.0, "damage": 30},
    "dolphin": {"name": "海豚骑士", "hp": 290, "speed": 30.0, "damage": 32},
}"""

new_zombies_end = """    "ducky": {"name": "救生圈鸭鸭", "hp": 180, "speed": 17.0, "damage": 28},
    "snorkel": {"name": "潜水僵尸", "hp": 210, "speed": 19.0, "damage": 30},
    "dolphin": {"name": "海豚骑士", "hp": 290, "speed": 30.0, "damage": 32},
    "gargantuar": {"name": "巨人僵尸", "hp": 3000, "speed": 11.0, "damage": 1500},
    "imp": {"name": "小鬼僵尸", "hp": 90, "speed": 38.0, "damage": 25},
    "balloon": {"name": "气球僵尸", "hp": 140, "speed": 17.0, "damage": 28},
    "jackbox": {"name": "小丑僵尸", "hp": 240, "speed": 28.0, "damage": 30},
    "digger": {"name": "矿工僵尸", "hp": 220, "speed": 22.0, "damage": 30},
}"""

if old_zombies_end in code:
    code = code.replace(old_zombies_end, new_zombies_end)
    print("ZOMBIES expanded!")

# 3. 扩充 UNLOCK_ORDER (34 种植物完整时序)
old_unlock_order = """UNLOCK_ORDER = [
    # 初始基础植物 (第 1 关开局可用)
    "sunflower",
    "peashooter",
    # 白天草坪阶段解锁 (第 1~5 关通关赠送，白天绝不出现蘑菇！)
    "wallnut",
    "snowpea",
    "potatomine",
    "repeater",
    "squash",
    # 黑夜墓地阶段解锁 (第 6~10 关通关赠送，夜间专属蘑菇家族与防御杀器)
    "puffshroom",
    "sunshroom",
    "fumeshroom",
    "spikeweed",
    "hypnoshroom",
    "cherrybomb",
    "chomper",
    "iceshroom",
    "doomshroom",
    "jalapeno",
    # 泳池水面阶段解锁 (第 11~15 关通关赠送，水面两栖战力与强力投手)
    "lilypad",
    "cabbagepult",
    "kernelpult",
    "torchwood",
    "garlic",
    "cattail",
    "twinsunflower",
    "starfruit",
    "threepeater",
    "melonpult",
    "tallnut",
    # 无尽模式终极武器 (第 16 关无尽挑战通关终极战利品)
    "wintermelon",
    "gatlingpea",
]"""

new_unlock_order = """UNLOCK_ORDER = [
    # 初始基础植物 (第 1 关开局可用)
    "sunflower",
    "peashooter",
    # 白天草坪阶段解锁 (第 1~5 关通关赠送，白天绝不出现蘑菇！)
    "wallnut",
    "snowpea",
    "potatomine",
    "repeater",
    "squash",
    # 黑夜墓地阶段解锁 (第 6~10 关通关赠送，夜间专属蘑菇家族与防御杀器)
    "puffshroom",
    "sunshroom",
    "fumeshroom",
    "spikeweed",
    "hypnoshroom",
    "cherrybomb",
    "chomper",
    "iceshroom",
    "doomshroom",
    "jalapeno",
    # 泳池水面阶段解锁 (第 11~15 关通关赠送，水面两栖战力与强力投手)
    "lilypad",
    "cabbagepult",
    "kernelpult",
    "torchwood",
    "garlic",
    "cattail",
    "twinsunflower",
    "starfruit",
    "threepeater",
    "melonpult",
    "tallnut",
    # 传奇新植物与终极武器
    "agave",
    "magicshroom",
    "laserbean",
    "wintermelon",
    "gatlingpea",
    "cobcannon",
]"""

if old_unlock_order in code:
    code = code.replace(old_unlock_order, new_unlock_order)
    print("UNLOCK_ORDER expanded to 34 plants!")

# 4. 扩充 PLANT_TIPS
old_tips_end = """    "twinsunflower": "双子向日葵：双头并立双倍快乐！每次稳定产出 50 点巨量阳光，经济腾飞核心！",
    "starfruit": "杨桃：全方位无死角弹幕射手！同时向 5 个方向发射高速旋转飞星，密不透风！",
}"""

new_tips_end = """    "twinsunflower": "双子向日葵：双头并立双倍快乐！每次稳定产出 50 点巨量阳光，经济腾飞核心！",
    "starfruit": "杨桃：全方位无死角弹幕射手！同时向 5 个方向发射高速旋转飞星，密不透风！",
    "cobcannon": "玉米加农炮：PVZ 终极大杀器！装填高爆玉米核弹，轰炸全屏 3x3 范围造成 1800 毁天灭地巨额伤害！",
    "magicshroom": "魔术菇：挥舞魔杖连发旋转魔术扑克牌！命中时 25% 几率奇迹魅惑变节僵尸或掉落暴富阳光！",
    "agave": "龙舌兰：近战刺客与剑气宗师！拔出青翠多肉巨剑蓄力二连斩；对残血僵尸直接施展苍翠剑浪斩杀！",
    "laserbean": "激光豆：未来科幻双目射手！双眼射出贯通全屏整行的超强蓝色激光束，无视护甲穿透灼烧！",
}"""

if old_tips_end in code:
    code = code.replace(old_tips_end, new_tips_end)
    print("PLANT_TIPS expanded!")

# 5. 更新 LEVEL_REWARDS 融入新植物
old_rewards = """    13: {"plants": ["starfruit", "threepeater"], "artifact": None},
    14: {
        "plants": ["melonpult", "tallnut"],
        "artifact": "master_belt",
        "artifact_name": "大师战术腰带",
        "artifact_desc": "顶级战术大师腰带！出战卡槽容量永久扩充至 9 格！",
    },
    15: {"plants": ["wintermelon", "gatlingpea"], "artifact": None},"""

new_rewards = """    13: {"plants": ["starfruit", "threepeater", "agave"], "artifact": None},
    14: {
        "plants": ["melonpult", "tallnut", "magicshroom", "laserbean"],
        "artifact": "master_belt",
        "artifact_name": "大师战术腰带",
        "artifact_desc": "顶级战术大师腰带！出战卡槽容量永久扩充至 10 格！",
    },
    15: {"plants": ["wintermelon", "gatlingpea", "cobcannon"], "artifact": None},"""

if old_rewards in code:
    code = code.replace(old_rewards, new_rewards)
    print("LEVEL_REWARDS updated!")

# 6. 更新 Plant 和 Zombie 类字段
old_plant_fields = """    squash_target_x: float = 0.0
    cell_h: int = CELL_H
    carrier: "Plant | None" = None
    carried_plant: "Plant | None" = None"""

new_plant_fields = """    squash_target_x: float = 0.0
    cell_h: int = CELL_H
    carrier: "Plant | None" = None
    carried_plant: "Plant | None" = None
    cannon_ready: bool = True
    cannon_timer: float = 0.0
    agave_state: str = "idle"
    agave_timer: float = 0.0
    laser_timer: float = 0.0
    laser_active: float = 0.0"""

if old_plant_fields in code:
    code = code.replace(old_plant_fields, new_plant_fields)
    print("Plant fields updated!")

old_zombie_fields = """    butter_timer: float = 0.0
    is_submerged: bool = False
    has_dolphin: bool = False"""

new_zombie_fields = """    butter_timer: float = 0.0
    is_submerged: bool = False
    has_dolphin: bool = False
    hypnotized: bool = False
    has_imp: bool = True
    flying: bool = True
    jackbox_timer: float = 7.0
    digging: bool = False
    emerged: bool = False"""

if old_zombie_fields in code:
    code = code.replace(old_zombie_fields, new_zombie_fields)
    print("Zombie fields updated!")

# 7. 更新选卡目录排布为 9 列 x 4 行 (容纳 34 种植物)
old_catalog = """        # 30 Plants Catalog Grid (8 cols x 4 rows)
        unlocked = set(self.available_plants())
        cw = 98
        ch = 72
        gap_x = 12
        gap_y = 6
        gx0 = cat_rect.x + (cat_rect.width - (8 * cw + 7 * gap_x)) // 2
        gy0 = cat_rect.y + 60

        self.catalog_rects = {}
        hovered_plant = None
        for idx, name in enumerate(UNLOCK_ORDER):
            col = idx % 8
            row = idx // 8"""

new_catalog = """        # 34 Plants Catalog Grid (9 cols x 4 rows)
        unlocked = set(self.available_plants())
        cw = 88
        ch = 72
        gap_x = 8
        gap_y = 6
        gx0 = cat_rect.x + (cat_rect.width - (9 * cw + 8 * gap_x)) // 2
        gy0 = cat_rect.y + 60

        self.catalog_rects = {}
        hovered_plant = None
        for idx, name in enumerate(UNLOCK_ORDER):
            col = idx % 9
            row = idx // 9"""

if old_catalog in code:
    code = code.replace(old_catalog, new_catalog)
    print("Catalog grid updated to 9x4!")

# 8. 更新植物战斗行为逻辑 (_update_plants)
plant_logic_hook = """            elif plant.ptype == "starfruit":
                if plant.action_timer >= 1.4:
                    plant.action_timer = 0.0
                    if any(z.hp > 0 and z.x >= plant.x - 100 for z in self.zombies):
                        for angle_deg in (0, 72, 144, 216, 288):
                            rad = math.radians(angle_deg)
                            self.projectiles.append(
                                Projectile(
                                    plant.x + 8, plant.y - 10, plant.row, 20.0,
                                    bullet_type="star",
                                    angle=rad,
                                )
                            )
                        self.audio.play("plant")"""

plant_logic_new = """            elif plant.ptype == "starfruit":
                if plant.action_timer >= 1.4:
                    plant.action_timer = 0.0
                    if any(z.hp > 0 and z.x >= plant.x - 100 for z in self.zombies):
                        for angle_deg in (0, 72, 144, 216, 288):
                            rad = math.radians(angle_deg)
                            self.projectiles.append(
                                Projectile(
                                    plant.x + 8, plant.y - 10, plant.row, 20.0,
                                    bullet_type="star",
                                    angle=rad,
                                )
                            )
                        self.audio.play("plant")
            elif plant.ptype == "cobcannon":
                if not plant.cannon_ready:
                    plant.cannon_timer -= dt
                    if plant.cannon_timer <= 0:
                        plant.cannon_ready = True
                        self.float_text(plant.x, plant.y - 45, "加农炮就绪！", C_GOLD)
                else:
                    # 自动智能检测尸群聚集或高危精英
                    threats = [z for z in self.zombies if z.hp > 0 and 300 <= z.x <= 950]
                    if len(threats) >= 3 or any(z.ztype in ("gargantuar", "bucket", "runner") for z in threats):
                        target_z = max(threats, key=lambda z: z.hp)
                        plant.cannon_ready = False
                        plant.cannon_timer = 15.0
                        self.projectiles.append(
                            Projectile(
                                plant.x + 20, plant.y - 30, target_z.row, 1800.0,
                                speed=320.0,
                                bullet_type="cob_missile",
                                target_x=target_z.x,
                                target_y=lane_ground(target_z.row, cell_h=self.cell_h) - 40,
                            )
                        )
                        self.float_text(plant.x, plant.y - 50, "发射玉米核弹！", (255, 215, 60))
                        self.audio.play("explode")
            elif plant.ptype == "magicshroom":
                plant.action_timer += dt
                if plant.action_timer >= 1.3:
                    target = self._front_zombie_in_row(plant.row, plant.x)
                    if target is not None:
                        plant.action_timer = 0.0
                        suit = random.choice(["heart", "spade", "diamond", "club"])
                        self.projectiles.append(
                            Projectile(
                                plant.x + 18, plant.y - 12, plant.row, 35.0,
                                speed=460.0,
                                bullet_type="magic_card",
                                suit=suit,
                            )
                        )
                        self.audio.play("click")
            elif plant.ptype == "agave":
                # 近战 2 格内蓄力斩
                close_zombies = [z for z in self.zombies if z.row == plant.row and z.hp > 0 and plant.x <= z.x <= plant.x + CELL_W * 2.2]
                if close_zombies:
                    plant.agave_timer += dt
                    if plant.agave_timer >= 0.8:
                        plant.agave_timer = 0.0
                        # 施展双段剑气斩
                        for cz in close_zombies:
                            if cz.hp <= 100:
                                cz.hp = 0
                                self.float_text(cz.x, cz.y - 40, "绝杀斩！", (120, 255, 180))
                            else:
                                cz.hp -= 150.0
                                self.float_text(cz.x, cz.y - 35, "-150 剑气！", (150, 240, 200))
                            cz.flash = 0.25
                        self.burst(plant.x + 50, plant.y, (120, 255, 180), 20, upward=True)
                        self.audio.play("mower")
                else:
                    plant.agave_timer = 0.0
            elif plant.ptype == "laserbean":
                plant.laser_timer += dt
                if plant.laser_active > 0:
                    plant.laser_active -= dt
                elif plant.laser_timer >= 1.6:
                    target = self._front_zombie_in_row(plant.row, plant.x)
                    if target is not None:
                        plant.laser_timer = 0.0
                        plant.laser_active = 0.35
                        # 整行激光贯穿
                        for lz in self.zombies:
                            if lz.row == plant.row and lz.hp > 0 and lz.x >= plant.x - 20:
                                lz.hp -= 45.0
                                lz.flash = 0.30
                                self.float_text(lz.x, lz.y - 25, "激光穿透！", (80, 220, 255))
                        self.audio.play("mower")"""

if plant_logic_hook in code:
    code = code.replace(plant_logic_hook, plant_logic_new)
    print("Plant combat logic updated!")

# 9. 更新 Projectile 属性
old_proj_dataclass = """@dataclass
class Projectile:
    x: float
    y: float
    row: int
    damage: float
    speed: float = 430.0
    freeze: bool = False
    alive: bool = True
    bullet_type: str = "pea"
    arc_progress: float = 0.0
    start_x: float = 0.0
    start_y: float = 0.0
    target_x: float = 0.0
    target_y: float = 0.0
    splash_radius: float = 0.0
    angle: float = 0.0"""

new_proj_dataclass = """@dataclass
class Projectile:
    x: float
    y: float
    row: int
    damage: float
    speed: float = 430.0
    freeze: bool = False
    alive: bool = True
    bullet_type: str = "pea"
    arc_progress: float = 0.0
    start_x: float = 0.0
    start_y: float = 0.0
    target_x: float = 0.0
    target_y: float = 0.0
    splash_radius: float = 0.0
    angle: float = 0.0
    suit: str = "heart" """

if old_proj_dataclass in code:
    code = code.replace(old_proj_dataclass, new_proj_dataclass)
    print("Projectile dataclass updated!")

# 10. 子弹更新循环中增加 cob_missile 与 magic_card 逻辑
old_update_proj_star = """            elif projectile.bullet_type == "star":
                projectile.x += math.cos(projectile.angle) * projectile.speed * dt
                projectile.y += math.sin(projectile.angle) * projectile.speed * dt
                if not (0 <= projectile.x <= WIDTH and 0 <= projectile.y <= HEIGHT):
                    projectile.alive = False
                    continue"""

new_update_proj_star = """            elif projectile.bullet_type == "star":
                projectile.x += math.cos(projectile.angle) * projectile.speed * dt
                projectile.y += math.sin(projectile.angle) * projectile.speed * dt
                if not (0 <= projectile.x <= WIDTH and 0 <= projectile.y <= HEIGHT):
                    projectile.alive = False
                    continue
            elif projectile.bullet_type == "cob_missile":
                projectile.arc_progress += dt * 1.25
                prog = min(1.0, projectile.arc_progress)
                projectile.x = lerp(projectile.start_x, projectile.target_x, prog)
                arc_h = -220.0 * math.sin(prog * math.pi)
                projectile.y = lerp(projectile.start_y, projectile.target_y, prog) + arc_h
                if prog >= 1.0:
                    projectile.alive = False
                    self.explode_at(projectile.target_x, projectile.target_y, 1800.0, 150.0)
                    self.burst(projectile.target_x, projectile.target_y, (255, 215, 60), 36)
                    self.burst(projectile.target_x, projectile.target_y, (255, 120, 40), 24)
                    self.audio.play("explode")
                    continue
                continue
            elif projectile.bullet_type == "magic_card":
                projectile.x += projectile.speed * dt
                if projectile.x > WIDTH + 50:
                    projectile.alive = False
                    continue"""

if old_update_proj_star in code:
    code = code.replace(old_update_proj_star, new_update_proj_star)
    print("Projectile update loop updated!")

# 11. 命中判定中增加气球僵尸与魔术奇迹
old_hit_check = """            if abs(projectile.x - zombie.x) > 28:
                continue"""

new_hit_check = """            # 气球僵尸浮空避开普通地面直线豌豆
            if getattr(zombie, "ztype", "") == "balloon" and getattr(zombie, "flying", True):
                if projectile.bullet_type in ("pea", "fume"):
                    continue

            # 矿工潜行免疫正面射弹
            if getattr(zombie, "ztype", "") == "digger" and getattr(zombie, "digging", False):
                continue

            if abs(projectile.x - zombie.x) > 28:
                continue"""

if old_hit_check in code:
    code = code.replace(old_hit_check, new_hit_check)
    print("Hit check updated for balloon & digger!")

# 12. 魔术菇扑克牌命中特写
old_pea_hit = """            zombie.flash = 0.22
            zombie.hp -= projectile.damage
            projectile.alive = False"""

new_pea_hit = """            zombie.flash = 0.22
            zombie.hp -= projectile.damage
            projectile.alive = False

            if projectile.bullet_type == "magic_card":
                # 25% 概率魔术奇迹
                if random.random() < 0.25:
                    if zombie.ztype in ("basic", "cone") and not getattr(zombie, "hypnotized", False):
                        zombie.hypnotized = True
                        zombie.speed = -abs(zombie.speed)
                        self.float_text(zombie.x, zombie.y - 30, "魔术变节！", (255, 140, 220))
                    else:
                        self.suns.append(SunToken(zombie.x, zombie.y - 20, 25, self.time_value))
                        self.float_text(zombie.x, zombie.y - 30, "+25 魔术阳光！", C_SUN)

            # 击破气球落入地面
            if getattr(zombie, "ztype", "") == "balloon" and getattr(zombie, "flying", True):
                zombie.flying = False
                self.float_text(zombie.x, zombie.y - 35, "气球击破！", (255, 80, 80))
                self.burst(zombie.x, zombie.y - 20, (255, 60, 60), 16)"""

if old_pea_hit in code:
    code = code.replace(old_pea_hit, new_pea_hit)
    print("Magic card and balloon pop hits updated!")

# 13. 僵尸移动更新 (_update_zombies) 增加巨人砸扁与扔小鬼、小丑自爆、矿工潜行
old_zombie_eat = """            if zombie.eating > 0:
                zombie.eating = max(0.0, zombie.eating - dt)
                continue"""

new_zombie_eat = """            # 巨人僵尸半血抛掷小鬼
            if zombie.ztype == "gargantuar" and getattr(zombie, "has_imp", True) and zombie.hp <= 1500:
                zombie.has_imp = False
                throw_col = random.randint(2, 4)
                throw_x = GRID_X + throw_col * CELL_W + 40
                imp = Zombie("imp", zombie.row, throw_x, 90, 90, 38.0, 25.0, cell_h=self.cell_h)
                self.zombies.append(imp)
                self.float_text(zombie.x, zombie.y - 50, "抛掷小鬼！", (255, 100, 80))

            # 玩偶匣小丑自爆倒计时
            if zombie.ztype == "jackbox":
                zombie.jackbox_timer -= dt
                if zombie.jackbox_timer <= 0:
                    zombie.hp = 0
                    self.explode_at(zombie.x, zombie.y, 1800.0, 140.0)
                    self.float_text(zombie.x, zombie.y - 40, "八音盒自爆！", (255, 60, 40))
                    self.burst(zombie.x, zombie.y, (255, 80, 50), 30)
                    self.audio.play("explode")
                    continue

            # 矿工僵尸遁地与破土
            if zombie.ztype == "digger":
                if not zombie.emerged:
                    zombie.digging = True
                    zombie.x -= zombie.speed * dt
                    if zombie.x <= GRID_X + 20:
                        zombie.emerged = True
                        zombie.digging = False
                        zombie.speed = -abs(zombie.speed)
                        self.float_text(zombie.x, zombie.y - 40, "破土而出！", (180, 130, 80))
                        self.burst(zombie.x, zombie.y, (140, 90, 40), 20)
                    continue

            if zombie.eating > 0:
                zombie.eating = max(0.0, zombie.eating - dt)
                continue"""

if old_zombie_eat in code:
    code = code.replace(old_zombie_eat, new_zombie_eat)
    print("Zombie movement & abilities updated!")

# 14. 巨人一锤重砸秒杀植物
old_plant_damage = """            target_plant.hp -= zombie.damage * dt"""

new_plant_damage = """            # 巨人一击必杀粉碎植物
            dmg = 1500.0 if zombie.ztype == "gargantuar" else zombie.damage
            target_plant.hp -= dmg * dt
            if zombie.ztype == "gargantuar":
                self.burst(target_plant.x, target_plant.y, (120, 180, 80), 18)"""

if old_plant_damage in code:
    code = code.replace(old_plant_damage, new_plant_damage)
    print("Gargantuar smash damage updated!")

pvz_path.write_text(code, encoding="utf-8")
print("Full expansion patch applied successfully!")
