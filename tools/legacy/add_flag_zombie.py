# -*- coding: utf-8 -*-
from pathlib import Path

p = Path(r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\pvz_ten_levels.py")
code = p.read_text(encoding="utf-8")

old_s = '"basic": {"name": "普通僵尸", "hp": 170, "speed": 18.0, "damage": 28},'
new_s = '"basic": {"name": "普通僵尸", "hp": 170, "speed": 18.0, "damage": 28},\n    "flag": {"name": "旗帜领队僵尸", "hp": 190, "speed": 22.0, "damage": 28},'

if old_s in code:
    code = code.replace(old_s, new_s)
    p.write_text(code, encoding="utf-8")
    print("Flag zombie added!")
