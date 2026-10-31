# -*- coding: utf-8 -*-
from pathlib import Path

p = Path(r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\pvz_ten_levels.py")
code = p.read_text(encoding="utf-8")

old_part = """                                    if is_ice:
                                        z.slow_timer = 6.0
                continue"""

new_part = """                                    if is_ice:
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
                continue"""

if old_part in code:
    code = code.replace(old_part, new_part)
    p.write_text(code, encoding="utf-8")
    print("Cob missile impact logic inserted successfully!")
else:
    print("old_part not found!")
