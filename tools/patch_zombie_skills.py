# -*- coding: utf-8 -*-
from pathlib import Path

p = Path(r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\pvz_ten_levels.py")
code = p.read_text(encoding="utf-8")

old_vault_end = """                    continue

            zombie.slow_timer = max(0.0, zombie.slow_timer - dt)"""

new_vault_end = """                    continue

            # 巨人半血抛掷小鬼
            if zombie.ztype == "gargantuar" and getattr(zombie, "has_imp", True) and zombie.hp <= 1500:
                zombie.has_imp = False
                throw_col = 3
                throw_x = GRID_X + throw_col * CELL_W + 40
                imp = Zombie("imp", zombie.row, throw_x, 90, 90, 38.0, 25.0, cell_h=self.cell_h)
                self.zombies.append(imp)
                self.float_text(zombie.x, zombie.y - 50, "抛掷小鬼！", (255, 100, 80))

            # 小丑八音盒倒计时自爆
            if zombie.ztype == "jackbox":
                zombie.jackbox_timer = getattr(zombie, "jackbox_timer", 7.0) - dt
                if zombie.jackbox_timer <= 0:
                    zombie.hp = 0
                    zombie.dead = True
                    self.burst(zombie.x, zombie.y, (255, 80, 50), 30)
                    self.audio.play("cherrybomb")
                    self.float_text(zombie.x, zombie.y - 40, "八音盒自爆！", (255, 60, 40))
                    for p_item in self.plants:
                        if p_item.alive and abs(p_item.x - zombie.x) <= CELL_W * 1.5 and abs(p_item.row - zombie.row) <= 1:
                            p_item.alive = False
                    continue

            # 矿工遁地潜行破土
            if zombie.ztype == "digger":
                if not getattr(zombie, "emerged", False):
                    zombie.digging = True
                    zombie.x -= zombie.speed * dt
                    if zombie.x <= GRID_X + 25:
                        zombie.emerged = True
                        zombie.digging = False
                        zombie.speed = -abs(zombie.speed)
                        self.float_text(zombie.x, zombie.y - 40, "破土而出！", (180, 130, 80))
                        self.burst(zombie.x, zombie.y, (140, 90, 40), 20)
                    continue

            zombie.slow_timer = max(0.0, zombie.slow_timer - dt)"""

if old_vault_end in code:
    code = code.replace(old_vault_end, new_vault_end)
    print("Zombie special skills injected!")
else:
    print("old_vault_end not found!")

# 巨人一击必杀植物
old_plant_bite = "plant.hp -= zombie.damage * (1.5 if zombie.enraged else 1.0)"
new_plant_bite = """dmg = 1500.0 if zombie.ztype == "gargantuar" else (zombie.damage * (1.5 if zombie.enraged else 1.0))
                    plant.hp -= dmg
                    if zombie.ztype == "gargantuar":
                        self.burst(plant.x, plant.y, (140, 180, 80), 16)
                        self.audio.play("squash")"""

if old_plant_bite in code:
    code = code.replace(old_plant_bite, new_plant_bite)
    print("Gargantuar smash bite injected!")

p.write_text(code, encoding="utf-8")
print("Done!")
