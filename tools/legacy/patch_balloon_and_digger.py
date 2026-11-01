# -*- coding: utf-8 -*-
from pathlib import Path

p = Path(r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\pvz_ten_levels.py")
code = p.read_text(encoding="utf-8")

old_submerged = """                # 潜水中的潜水僵尸免疫水平直射
                if getattr(zombie, "is_submerged", False):
                    continue"""

new_submerged = """                # 潜水中的潜水僵尸免疫水平直射
                if getattr(zombie, "is_submerged", False):
                    continue

                # 浮空气球僵尸免疫普通水平直射豌豆
                if getattr(zombie, "ztype", "") == "balloon" and getattr(zombie, "flying", True):
                    if projectile.bullet_type in ("pea", "fire_pea", "snowpea"):
                        continue
                    else:
                        zombie.flying = False
                        self.float_text(zombie.x, zombie.y - 35, "气球击破！", (255, 80, 80))
                        self.burst(zombie.x, zombie.y - 20, (255, 60, 60), 16)

                # 矿工遁地潜行免疫正面子弹
                if getattr(zombie, "ztype", "") == "digger" and getattr(zombie, "digging", False):
                    continue"""

if old_submerged in code:
    code = code.replace(old_submerged, new_submerged)
    print("Straight projectile hit check updated for balloon & digger!")

# 投掷物击破气球
old_cabbage_hit = """                    if projectile.bullet_type == "cabbage":
                        self.burst(impact_x, impact_y, (140, 210, 80), 8)
                        if main_target:
                            self._damage_zombie(main_target, projectile.damage, freeze=False)"""

new_cabbage_hit = """                    if main_target and getattr(main_target, "ztype", "") == "balloon" and getattr(main_target, "flying", True):
                        main_target.flying = False
                        self.float_text(main_target.x, main_target.y - 35, "气球击破！", (255, 80, 80))
                        self.burst(main_target.x, main_target.y - 20, (255, 60, 60), 16)

                    if projectile.bullet_type == "cabbage":
                        self.burst(impact_x, impact_y, (140, 210, 80), 8)
                        if main_target:
                            self._damage_zombie(main_target, projectile.damage, freeze=False)"""

if old_cabbage_hit in code:
    code = code.replace(old_cabbage_hit, new_cabbage_hit)
    print("Lobbed projectile hit check updated for balloon!")

p.write_text(code, encoding="utf-8")
print("Done!")
