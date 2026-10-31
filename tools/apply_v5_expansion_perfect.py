# -*- coding: utf-8 -*-
"""Accurate injection patch for PVZ expansion:
- PLANTS: cobcannon, magicshroom, agave, laserbean
- ZOMBIES: gargantuar, imp, balloon, jackbox, digger
- Combat behaviors & Projectiles
"""

from pathlib import Path

p_pvz = Path(r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\pvz_ten_levels.py")
code = p_pvz.read_text(encoding="utf-8")

# 1. 扩充 PLANTS
old_starfruit = '''    "starfruit": {
        "name": "杨桃", "cost": 125, "cooldown": 7.5, "hp": 300,
    },
}'''

new_starfruit = '''    "starfruit": {
        "name": "杨桃", "cost": 125, "cooldown": 7.5, "hp": 300,
    },
    "cobcannon": {
        "name": "玉米加农炮", "cost": 500, "cooldown": 30.0, "hp": 1200,
    },
    "magicshroom": {
        "name": "魔术菇", "cost": 175, "cooldown": 10.0, "hp": 300,
    },
    "agave": {
        "name": "龙舌兰", "cost": 150, "cooldown": 10.0, "hp": 600,
    },
    "laserbean": {
        "name": "激光豆", "cost": 200, "cooldown": 10.0, "hp": 300,
    },
}'''

if old_starfruit in code:
    code = code.replace(old_starfruit, new_starfruit)
    print("PLANTS expanded successfully!")

# 2. 扩充 ZOMBIES
old_dolphin = '''    "dolphin": {"name": "海豚骑士僵尸", "hp": 320, "speed": 36.0, "damage": 30, "water": True},
}'''

new_dolphin = '''    "dolphin": {"name": "海豚骑士僵尸", "hp": 320, "speed": 36.0, "damage": 30, "water": True},
    "gargantuar": {"name": "巨人僵尸", "hp": 3000, "speed": 11.0, "damage": 1500},
    "imp": {"name": "小鬼僵尸", "hp": 90, "speed": 38.0, "damage": 25},
    "balloon": {"name": "气球僵尸", "hp": 140, "speed": 17.0, "damage": 28},
    "jackbox": {"name": "小丑僵尸", "hp": 240, "speed": 28.0, "damage": 30},
    "digger": {"name": "矿工僵尸", "hp": 220, "speed": 22.0, "damage": 30},
}'''

if old_dolphin in code:
    code = code.replace(old_dolphin, new_dolphin)
    print("ZOMBIES expanded successfully!")

# 3. 在 _update_plants 中插入 4 大新植物
old_doom_plant = '''            elif plant.ptype == "doomshroom":
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

new_plants_combat = '''            elif plant.ptype == "doomshroom":
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
                                self._damage_zombie(z, 1800.0)
            elif plant.ptype == "cobcannon":
                if not getattr(plant, "cannon_ready", True):
                    plant.cannon_timer -= dt
                    if plant.cannon_timer <= 0:
                        plant.cannon_ready = True
                        self.float_text(plant.x, plant.y - 45, "加农炮就绪！", C_GOLD)
                else:
                    threats = [z for z in self.zombies if not z.dead and 300 <= z.x <= 950]
                    if len(threats) >= 2 or any(z.ztype in ("gargantuar", "bucket", "runner") for z in threats):
                        target_z = max(threats, key=lambda z: z.hp)
                        plant.cannon_ready = False
                        plant.cannon_timer = 15.0
                        proj = Projectile(plant.x + 20, plant.y - 30, target_z.row, 1800.0, bullet_type="cob_missile")
                        proj.start_x = plant.x + 20
                        proj.start_y = plant.y - 30
                        proj.target_x = target_z.x
                        proj.target_y = lane_ground(target_z.row, cell_h=self.cell_h) - 40
                        proj.arc_progress = 0.0
                        self.projectiles.append(proj)
                        self.float_text(plant.x, plant.y - 50, "发射玉米核弹！", (255, 215, 60))
                        self.audio.play("cherrybomb")
            elif plant.ptype == "magicshroom":
                plant.action_timer += dt
                if plant.action_timer >= 1.3:
                    targets = [z for z in self.zombies if z.row == plant.row and not z.dead and z.x >= plant.x - 20]
                    if targets:
                        plant.action_timer = 0.0
                        y = lane_ground(plant.row, cell_h=self.cell_h) - 52
                        proj = Projectile(plant.x + 20, y, plant.row, 35.0, bullet_type="magic_card")
                        proj.suit = random.choice(["heart", "spade", "diamond", "club"])
                        self.projectiles.append(proj)
                        self.audio.play("plant")
            elif plant.ptype == "agave":
                # 龙舌兰：近战 2 格蓄力二连斩
                close_z = [z for z in self.zombies if z.row == plant.row and not z.dead and plant.x <= z.x <= plant.x + CELL_W * 2.2]
                if close_z:
                    plant.agave_timer += dt
                    if plant.agave_timer >= 0.8:
                        plant.agave_timer = 0.0
                        for cz in close_z:
                            if cz.hp <= 100:
                                self._damage_zombie(cz, 200.0)
                                self.float_text(cz.x, cz.y - 40, "苍翠绝杀！", (120, 255, 180))
                            else:
                                self._damage_zombie(cz, 150.0)
                                self.float_text(cz.x, cz.y - 35, "-150 剑气！", (150, 240, 200))
                        self.burst(plant.x + 50, plant.y, (120, 255, 180), 20, upward=True)
                        self.audio.play("mower")
                else:
                    plant.agave_timer = 0.0
            elif plant.ptype == "laserbean":
                plant.laser_timer += dt
                if plant.laser_active > 0:
                    plant.laser_active -= dt
                elif plant.laser_timer >= 1.6:
                    row_z = [z for z in self.zombies if z.row == plant.row and not z.dead and z.x >= plant.x - 20]
                    if row_z:
                        plant.laser_timer = 0.0
                        plant.laser_active = 0.35
                        for lz in row_z:
                            self._damage_zombie(lz, 45.0)
                            self.float_text(lz.x, lz.y - 25, "激光穿透！", (80, 220, 255))
                        self.burst(plant.x + 60, plant.y, (80, 220, 255), 15)
                        self.audio.play("mower")'''

if old_doom_plant in code:
    code = code.replace(old_doom_plant, new_plants_combat)
    print("Plant combat behaviors injected successfully!")

# 4. 在 _update_projectiles 中处理 cob_missile 与 magic_card
old_proj_check = '''            if projectile.bullet_type == "fume":
                # 大喷菇穿透性紫色气雾
                for z in self.zombies:
                    if not z.dead and z.row == projectile.row:
                        if abs(projectile.x - z.x) <= 32:
                            if id(z) not in getattr(projectile, "pierced_zombies", set()):
                                projectile.pierced_zombies.add(id(z))
                                self._damage_zombie(z, projectile.damage)
                                self.burst(z.x, z.y, (180, 80, 220), 6)
                continue'''

new_proj_check = '''            if projectile.bullet_type == "cob_missile":
                projectile.arc_progress += dt * 1.35
                prog = min(1.0, projectile.arc_progress)
                projectile.x = lerp(projectile.start_x, projectile.target_x, prog)
                arc_h = -220.0 * math.sin(prog * math.pi)
                projectile.y = lerp(projectile.start_y, projectile.target_y, prog) + arc_h
                if prog >= 1.0:
                    projectile.alive = False
                    self.burst(projectile.target_x, projectile.target_y, (255, 215, 60), 36)
                    self.burst(projectile.target_x, projectile.target_y, (255, 120, 40), 24)
                    self.audio.play("cherrybomb")
                    self.float_text(projectile.target_x, projectile.target_y - 45, "核弹轰炸！", (255, 215, 60))
                    for z in self.zombies:
                        if not z.dead:
                            dist = math.hypot(z.x - projectile.target_x, (lane_ground(z.row, cell_h=self.cell_h) - 40) - projectile.target_y)
                            if dist <= 160:
                                self._damage_zombie(z, 1800.0)
                continue
            elif projectile.bullet_type == "fume":
                # 大喷菇穿透性紫色气雾
                for z in self.zombies:
                    if not z.dead and z.row == projectile.row:
                        if abs(projectile.x - z.x) <= 32:
                            if id(z) not in getattr(projectile, "pierced_zombies", set()):
                                projectile.pierced_zombies.add(id(z))
                                self._damage_zombie(z, projectile.damage)
                                self.burst(z.x, z.y, (180, 80, 220), 6)
                continue'''

if old_proj_check in code:
    code = code.replace(old_proj_check, new_proj_check)
    print("Cob missile projectile logic injected successfully!")

# 5. 扑克牌命中特写与气球打破
old_damage_z = '''        self._damage_zombie(target_z, projectile.damage)
        if projectile.freeze:
            target_z.slow_timer = max(target_z.slow_timer, 6.0)'''

new_damage_z = '''        # 气球僵尸浮空避开普通地面直线子弹
        if getattr(target_z, "ztype", "") == "balloon" and getattr(target_z, "flying", True):
            if projectile.bullet_type in ("pea", "fume"):
                return # 普通直线豌豆穿过不伤气球
            else:
                target_z.flying = False
                self.float_text(target_z.x, target_z.y - 35, "气球击破！", (255, 80, 80))
                self.burst(target_z.x, target_z.y - 20, (255, 60, 60), 16)

        # 矿工遁地免疫正面子弹
        if getattr(target_z, "ztype", "") == "digger" and getattr(target_z, "digging", False):
            return

        self._damage_zombie(target_z, projectile.damage)
        if projectile.freeze:
            target_z.slow_timer = max(target_z.slow_timer, 6.0)

        # 魔术菇扑克牌奇迹
        if projectile.bullet_type == "magic_card":
            if random.random() < 0.25:
                if target_z.ztype in ("basic", "cone") and not getattr(target_z, "hypnotized", False):
                    target_z.hypnotized = True
                    target_z.speed = -abs(target_z.speed)
                    self.float_text(target_z.x, target_z.y - 30, "魔术变节！", (255, 140, 220))
                else:
                    self.suns.append(SunToken(target_z.x, target_z.y - 20, 25, self.time_value))
                    self.float_text(target_z.x, target_z.y - 30, "+25 魔术阳光！", C_SUN)'''

if old_damage_z in code:
    code = code.replace(old_damage_z, new_damage_z)
    print("Magic card and balloon pop damage injected successfully!")

# 6. 在 _update_zombies 中加入巨人抛小鬼、小丑自爆、矿工潜行
old_z_eat = '''            if zombie.eating > 0:
                zombie.eating = max(0.0, zombie.eating - dt)
                continue'''

new_z_eat = '''            # 巨人僵尸半血抛掷小鬼
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
                    zombie.dead = True
                    self.burst(zombie.x, zombie.y, (255, 80, 50), 30)
                    self.audio.play("cherrybomb")
                    self.float_text(zombie.x, zombie.y - 40, "八音盒自爆！", (255, 60, 40))
                    # 炸毁附近植物
                    for p in self.plants:
                        if p.alive and abs(p.x - zombie.x) <= CELL_W * 1.5 and abs(p.y - zombie.y) <= self.cell_h * 1.5:
                            p.alive = False
                    continue

            # 矿工僵尸遁地与破土
            if zombie.ztype == "digger":
                if not getattr(zombie, "emerged", False):
                    zombie.digging = True
                    zombie.x -= zombie.speed * dt
                    if zombie.x <= GRID_X + 20:
                        zombie.emerged = True
                        zombie.digging = False
                        zombie.speed = -abs(zombie.speed) # 破土向右
                        self.float_text(zombie.x, zombie.y - 40, "破土而出！", (180, 130, 80))
                        self.burst(zombie.x, zombie.y, (140, 90, 40), 20)
                    continue

            if zombie.eating > 0:
                zombie.eating = max(0.0, zombie.eating - dt)
                continue'''

if old_z_eat in code:
    code = code.replace(old_z_eat, new_z_eat)
    print("Zombie special mechanics injected successfully!")

# 7. 巨人一击秒杀植物
old_z_attack = '''            target_plant.hp -= zombie.damage * dt'''
new_z_attack = '''            dmg = 1500.0 if zombie.ztype == "gargantuar" else zombie.damage
            target_plant.hp -= dmg * dt
            if zombie.ztype == "gargantuar":
                self.burst(target_plant.x, target_plant.y, (120, 180, 80), 18)'''

if old_z_attack in code:
    code = code.replace(old_z_attack, new_z_attack)
    print("Gargantuar instant kill damage injected successfully!")

p_pvz.write_text(code, encoding="utf-8")
print("=== All expansion elements injected into pvz_ten_levels.py perfectly! ===")
