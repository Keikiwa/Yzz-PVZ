# -*- coding: utf-8 -*-
import os

path = r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\pvz_ten_levels.py"
with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. 标题副标题
target1 = 'text(self.screen, "PYGAME  ·  全功能豪华版  ·  草坪与泳池十六关", self.fonts.get(17, True), (255, 225, 137), (600, 96), "midtop")'
replacement1 = 'text(self.screen, "PVZ  ·  Gemini 4 Argon 复刻版本  ·  Python / Pygame 机制重制", self.fonts.get(17, True), (255, 225, 137), (600, 96), "midtop")'

# 2. 窗口标题
target2 = 'pygame.display.set_caption("植物大战僵尸 · 豪华增强版 · pygame")'
replacement2 = 'pygame.display.set_caption("植物大战僵尸 · Gemini 4 Argon 复刻版")'

# 3. 参数解析器描述
target3 = 'parser = argparse.ArgumentParser(description="植物大战僵尸风格 pygame 豪华版原型")'
replacement3 = 'parser = argparse.ArgumentParser(description="植物大战僵尸 - Gemini 4 Argon 复刻版 (Pygame)")'

# 4. 植物描述谦逊化
target4 = '"gatlingpea": "机枪射手：头戴钢盔的终极射手！一次性扫射 4 颗豌豆，配合火炬树桩火力毁天灭地！",'
replacement4 = '"gatlingpea": "机枪射手：头戴钢盔的四发重型射手，连续扫射 4 颗豌豆，配合火炬树桩火力倍增。",'

target5 = '"cobcannon": "玉米加农炮：PVZ 终极大杀器！装填高爆玉米核弹，轰炸全屏 3x3 范围造成 1800 毁天灭地巨额伤害！",'
replacement5 = '"cobcannon": "玉米加农炮：手动选点轰炸，落点周围 3x3 范围造成 1800 点高额范围爆炸伤害。",'

target6 = '"subtitle": "全兵种终极大决战！守住全场"'
replacement6 = '"subtitle": "全兵种防守演练！守住全场"'

assert target1 in code, "target1 not found"
assert target2 in code, "target2 not found"
assert target3 in code, "target3 not found"
assert target4 in code, "target4 not found"
assert target5 in code, "target5 not found"
assert target6 in code, "target6 not found"

code = code.replace(target1, replacement1, 1)
code = code.replace(target2, replacement2, 1)
code = code.replace(target3, replacement3, 1)
code = code.replace(target4, replacement4, 1)
code = code.replace(target5, replacement5, 1)
code = code.replace(target6, replacement6, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(code)

print("Successfully updated game text to modest PVZ - Gemini 4 Argon remake branding!")
