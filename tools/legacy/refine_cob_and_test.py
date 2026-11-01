# -*- coding: utf-8 -*-
"""Refine cob cannon projectile logic in pvz_ten_levels.py to match native lobbed physics."""

from pathlib import Path

p_pvz = Path(r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\pvz_ten_levels.py")
code = p_pvz.read_text(encoding="utf-8")

# 1. 更新加农炮发射参数为 is_lobbed
old_cob_launch = '''                        proj = Projectile(plant.x + 20, plant.y - 30, target_z.row, 1800.0, bullet_type="cob_missile")
                        proj.start_x = plant.x + 20
                        proj.start_y = plant.y - 30
                        proj.target_x = target_z.x
                        proj.target_y = lane_ground(target_z.row, cell_h=self.cell_h) - 40
                        proj.arc_progress = 0.0'''

new_cob_launch = '''                        proj = Projectile(plant.x + 20, plant.y - 30, target_z.row, 1800.0, bullet_type="cob_missile")
                        proj.is_lobbed = True
                        proj.start_x = plant.x + 20
                        proj.start_y = plant.y - 30
                        proj.target_x = target_z.x
                        proj.target_y = lane_ground(target_z.row, cell_h=self.cell_h) - 40
                        proj.lob_progress = 0.0
                        proj.lob_duration = 0.8
                        proj.apex_h = 240.0'''

if old_cob_launch in code:
    code = code.replace(old_cob_launch, new_cob_launch)
    print("Cob missile launch parameters updated!")

# 2. 在 is_lobbed 结算中加入 cob_missile 爆炸
old_melon_impact = '''                                    if is_ice:
                                        z.slow_timer = 6.0
                    continue'''

new_melon_impact = '''                                    if is_ice:
                                        z.slow_timer = 6.0
                    elif projectile.bullet_type == "cob_missile":
                        self.burst(impact_x, impact_y, (255, 215, 60), 36)
                        self.burst(impact_x, impact_y, (255, 120, 40), 24)
                        self.audio.play("cherrybomb")
                        self.float_text(impact_x, impact_y - 45, "核弹轰炸！", (255, 215, 60))
                        for z in self.zombies:
                            if not z.dead:
                                if abs(z.row - projectile.row) <= 1 and abs(z.x - impact_x) <= 150:
                                    self._damage_zombie(z, 1800.0)
                    continue'''

if old_melon_impact in code:
    code = code.replace(old_melon_impact, new_melon_impact)
    print("Cob missile lobbed impact logic added!")

p_pvz.write_text(code, encoding="utf-8")
print("pvz_ten_levels.py refined successfully!")
