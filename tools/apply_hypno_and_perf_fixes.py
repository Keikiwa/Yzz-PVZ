# -*- coding: utf-8 -*-
"""一键实装：
1. 魅惑菇倒戈僵尸双向啃食与对撞互相攻击机制
2. 植物与子弹友军保护（绝不误伤魅惑僵尸）
3. 全系统性能优化（Windows 1ms 定时器、2048 音频缓冲区、DOUBLEBUF 硬件双缓冲、文字短路缓存、内存防膨胀）
4. 魅惑僵尸朝向镜像翻转与彩虹倒戈特效
"""
import os
import re

GAME_PY = r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\pvz_ten_levels.py"
GRAPH_PY = r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\pvz_graphics.py"

with open(GAME_PY, "r", encoding="utf-8") as f:
    game_code = f.read()

with open(GRAPH_PY, "r", encoding="utf-8") as f:
    graph_code = f.read()

print("Applying performance & hypno patches...")

# -------------------------------------------------------------
# 1. Windows 1ms 定时器精度注入
# -------------------------------------------------------------
win_timer_inject = """import ctypes
try:
    ctypes.windll.winmm.timeBeginPeriod(1)
except Exception:
    pass
"""
if "timeBeginPeriod" not in game_code:
    game_code = win_timer_inject + "\n" + game_code

# -------------------------------------------------------------
# 2. 增大音频缓冲区到 2048，彻底根除音频欠载引起的周期性卡顿
# -------------------------------------------------------------
game_code = game_code.replace("buffer=512", "buffer=2048")

# -------------------------------------------------------------
# 3. 启用硬件双缓冲 DOUBLEBUF | HWSURFACE
# -------------------------------------------------------------
old_flags = """    flags = 0
    screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)"""
new_flags = """    flags = pygame.DOUBLEBUF | pygame.HWSURFACE
    try:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
    except Exception:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), 0)"""
if old_flags in game_code:
    game_code = game_code.replace(old_flags, new_flags, 1)

# -------------------------------------------------------------
# 4. 文字短路缓存加速 (彻底削减每帧 2000+ 次正则与渲染开销)
# -------------------------------------------------------------
old_text_def = """def text(
    surface: pygame.Surface,
    value: str,
    font: pygame.font.Font,
    color: tuple[int, int, int],
    pos: tuple[float, float],
    anchor: str = "topleft",
    shadow: tuple[int, int, int] | None = None,
) -> pygame.Rect:
    value = _clean_text_glyphs(value)
    key = (id(font), value, color)"""

new_text_def = """def text(
    surface: pygame.Surface,
    value: str,
    font: pygame.font.Font,
    color: tuple[int, int, int],
    pos: tuple[float, float],
    anchor: str = "topleft",
    shadow: tuple[int, int, int] | None = None,
) -> pygame.Rect:
    key = (id(font), value, color)
    image = _TEXT_CACHE.get(key)
    if image is None:
        value = _clean_text_glyphs(value)
        key = (id(font), value, color)
        image = _TEXT_CACHE.get(key)"""

if old_text_def in game_code:
    game_code = game_code.replace(old_text_def, new_text_def, 1)

# -------------------------------------------------------------
# 5. 魅惑僵尸双向面对面互啃机制 (彻底解决无法互相攻击啃食的问题)
# -------------------------------------------------------------
old_zombie_attack_block = """            if plant is not None:
                zombie.eating = min(1.0, zombie.eating + dt * 4)
                zombie.bite_timer += dt
                bite_delay = 0.38 if zombie.enraged else 0.55
                if zombie.bite_timer >= bite_delay:
                    zombie.bite_timer = 0
                    dmg = 1500.0 if zombie.ztype == "gargantuar" else (zombie.damage * (1.5 if zombie.enraged else 1.0))
                    plant.hp -= dmg
                    if zombie.ztype == "gargantuar":
                        self.burst(plant.x, plant.y, (140, 180, 80), 16)
                        self.audio.play("squash")
                    plant.flash = 0.18
                    self.burst(plant.x, plant.y, (120, 185, 75), 2)

                    # 魅惑菇：啃食即刻被魅惑倒戈
                    if plant.ptype == "hypnoshroom":
                        plant.alive = False
                        zombie.eating = 0.0
                        setattr(zombie, "hypnotized", True)
                        zombie.speed = -abs(zombie.speed) # 调头倒戈！
                        self.burst(plant.x, plant.y, (255, 120, 220), 16)
                        self.float_text(zombie.x, zombie.y - 25, "已被魅惑！", (255, 120, 220))
                        self.audio.play("groan")

                    # 大蒜啃咬分流变道
                    if plant.ptype == "garlic":
                        old_row = zombie.row
                        new_row = old_row
                        if getattr(self, "is_pool", False):
                            if old_row in (0, 1):
                                new_row = 1 if old_row == 0 else 0
                            elif old_row in (2, 3):
                                new_row = 3 if old_row == 2 else 2
                            elif old_row in (4, 5):
                                new_row = 5 if old_row == 4 else 4
                        else:
                            if old_row == 0:
                                new_row = 1
                            elif old_row == self.rows - 1:
                                new_row = old_row - 1
                            else:
                                new_row = old_row + random.choice([-1, 1])
                        if new_row != old_row:
                            zombie.row = new_row
                            zombie.eating = 0.0
                            self.burst(plant.x, plant.y, (240, 235, 200), 10)
                            self.float_text(zombie.x, zombie.y - 25, "嫌弃变道！", (230, 240, 180))

                    if plant.hp <= 0:
                        plant.alive = False
                        zombie.eating = 0.0
                        self.audio.play("click")
            else:
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
                elif zombie.x < MOWER_X - 6:
                    self.overlay = "lost"
                    self.lose_reason = f"第 {zombie.row + 1} 路的僵尸冲进了屋子！"
                    self.audio.stop_music()
                    self.audio.play("lose")
                    break"""

new_zombie_attack_block = """            is_hypno = getattr(zombie, "hypnotized", False)

            # 寻找敌对僵尸进行互相啃食对决
            target_enemy_z = None
            if is_hypno:
                # 魅惑僵尸朝右冲锋，咬右侧最近的普通敌方僵尸
                candidates = [
                    ez for ez in self.zombies
                    if not ez.dead and not getattr(ez, "hypnotized", False)
                    and ez.row == zombie.row
                    and -15 <= (ez.x - zombie.x) <= 45
                ]
                if candidates:
                    target_enemy_z = min(candidates, key=lambda ez: abs(ez.x - zombie.x))
            else:
                # 普通僵尸朝左前进，若面前遭遇倒戈的魅惑僵尸，必须停下啃食魅惑僵尸
                candidates = [
                    hz for hz in self.zombies
                    if not hz.dead and getattr(hz, "hypnotized", False)
                    and hz.row == zombie.row
                    and -15 <= (zombie.x - hz.x) <= 45
                ]
                if candidates:
                    target_enemy_z = min(candidates, key=lambda hz: abs(zombie.x - hz.x))

            # 执行战斗啃咬判定
            if target_enemy_z is not None:
                # 双方停下脚步，面对面激烈啃咬互殴！
                zombie.eating = min(1.0, zombie.eating + dt * 4)
                zombie.bite_timer += dt
                bite_delay = 0.38 if zombie.enraged else 0.50
                if zombie.bite_timer >= bite_delay:
                    zombie.bite_timer = 0
                    dmg = 1500.0 if zombie.ztype == "gargantuar" else (zombie.damage * (1.5 if zombie.enraged else 1.0))
                    self._damage_zombie(target_enemy_z, dmg)
                    target_enemy_z.flash = 0.18
                    self.burst(target_enemy_z.x, target_enemy_z.y - 15, (255, 120, 160), 4)
                    self.audio.play("chomp", cooldown=0.1)
            elif not is_hypno and plant is not None:
                # 普通僵尸正常啃食植物
                zombie.eating = min(1.0, zombie.eating + dt * 4)
                zombie.bite_timer += dt
                bite_delay = 0.38 if zombie.enraged else 0.55
                if zombie.bite_timer >= bite_delay:
                    zombie.bite_timer = 0
                    dmg = 1500.0 if zombie.ztype == "gargantuar" else (zombie.damage * (1.5 if zombie.enraged else 1.0))
                    plant.hp -= dmg
                    if zombie.ztype == "gargantuar":
                        self.burst(plant.x, plant.y, (140, 180, 80), 16)
                        self.audio.play("squash")
                    plant.flash = 0.18
                    self.burst(plant.x, plant.y, (120, 185, 75), 2)
                    self.audio.play("chomp", cooldown=0.1)

                    # 魅惑菇：啃食即刻被魅惑倒戈
                    if plant.ptype == "hypnoshroom":
                        plant.alive = False
                        zombie.eating = 0.0
                        setattr(zombie, "hypnotized", True)
                        zombie.speed = -abs(zombie.speed) # 彻底调头倒戈冲锋！
                        self.burst(plant.x, plant.y, (255, 120, 220), 20)
                        self.float_text(zombie.x, zombie.y - 25, "已被魅惑！", (255, 120, 220))
                        self.audio.play("groan")

                    # 大蒜啃咬分流变道
                    if plant.ptype == "garlic":
                        old_row = zombie.row
                        new_row = old_row
                        if getattr(self, "is_pool", False):
                            if old_row in (0, 1):
                                new_row = 1 if old_row == 0 else 0
                            elif old_row in (2, 3):
                                new_row = 3 if old_row == 2 else 2
                            elif old_row in (4, 5):
                                new_row = 5 if old_row == 4 else 4
                        else:
                            if old_row == 0:
                                new_row = 1
                            elif old_row == self.rows - 1:
                                new_row = old_row - 1
                            else:
                                new_row = old_row + random.choice([-1, 1])
                        if new_row != old_row:
                            zombie.row = new_row
                            zombie.eating = 0.0
                            self.burst(plant.x, plant.y, (240, 235, 200), 10)
                            self.float_text(zombie.x, zombie.y - 25, "嫌弃变道！", (230, 240, 180))

                    if plant.hp <= 0:
                        plant.alive = False
                        zombie.eating = 0.0
                        self.audio.play("click")
            else:
                # 移动阶段
                zombie.eating = max(0.0, zombie.eating - dt * 3)
                zombie.x -= zombie.speed * speed_mult * dt
                if is_hypno:
                    # 魅惑僵尸反推至右侧大门外后胜利撤退
                    if zombie.x > WIDTH + 80:
                        zombie.dead = True
                        continue
                elif zombie.x < MOWER_X - 6:
                    self.overlay = "lost"
                    self.lose_reason = f"第 {zombie.row + 1} 路的僵尸冲进了屋子！"
                    self.audio.stop_music()
                    self.audio.play("lose")
                    break"""

assert old_zombie_attack_block in game_code, "old_zombie_attack_block not matched!"
game_code = game_code.replace(old_zombie_attack_block, new_zombie_attack_block, 1)

# -------------------------------------------------------------
# 6. 植物索敌与子弹碰撞：排除魅惑僵尸 (友军保护)
# -------------------------------------------------------------
# 直线子弹与追踪尖刺碰撞
game_code = game_code.replace(
    "for zombie in self.zombies:\n                if zombie.dead:\n                    continue",
    "for zombie in self.zombies:\n                if zombie.dead or getattr(zombie, 'hypnotized', False):\n                    continue"
)

# 投掷物落地范围检测
game_code = game_code.replace(
    "z for z in self.zombies\n                        if z.row == projectile.row and not z.dead and abs(z.x - impact_x) < 55",
    "z for z in self.zombies\n                        if z.row == projectile.row and not z.dead and not getattr(z, 'hypnotized', False) and abs(z.x - impact_x) < 55"
)

# 大喷菇命中判定
game_code = game_code.replace(
    "if not ez.dead and ez.row == projectile.row and abs(ez.x - projectile.x) < 38 and id(ez) not in hit_set:",
    "if not ez.dead and not getattr(ez, 'hypnotized', False) and ez.row == projectile.row and abs(ez.x - projectile.x) < 38 and id(ez) not in hit_set:"
)

# 射手开火索敌判断
game_code = game_code.replace(
    "has_target = any(\n                        z.row == plant.row and not z.dead and z.x > plant.x - 20 and z.x <",
    "has_target = any(\n                        z.row == plant.row and not z.dead and not getattr(z, 'hypnotized', False) and z.x > plant.x - 20 and z.x <"
)

# 粒子系统上限防护 (最多 45 颗活跃粒子，杜绝粒子堆叠卡死)
particle_limit_check = """        self.particles = [p for p in self.particles if p.alive]
        if len(self.particles) > 45:
            self.particles = self.particles[-45:]"""
game_code = game_code.replace("self.particles = [p for p in self.particles if p.alive]", particle_limit_check)

with open(GAME_PY, "w", encoding="utf-8") as f:
    f.write(game_code)
print("Updated pvz_ten_levels.py!")

# -------------------------------------------------------------
# 7. pvz_graphics.py 魅惑僵尸渲染升级：面向翻转 + 彩虹魅惑光环
# -------------------------------------------------------------
target_zombie_render = """    # 死亡透明淡出支持
    if alpha < 255:
        scaled = _get_alpha_surf(scaled, alpha)"""

hypno_zombie_render = """    # 魅惑倒戈僵尸：水平镜像翻转（面向右侧），并附带梦幻彩虹倒戈光环
    is_hypno = getattr(zombie, "hypnotized", False)
    if is_hypno:
        scaled = pygame.transform.flip(scaled, True, False)

    # 死亡透明淡出支持
    if alpha < 255:
        scaled = _get_alpha_surf(scaled, alpha)"""

assert target_zombie_render in graph_code, "target_zombie_render not found in pvz_graphics.py"
graph_code = graph_code.replace(target_zombie_render, hypno_zombie_render, 1)

# 在绘制完 scaled 后，给魅惑僵尸加上流光紫粉光环
target_blit = """    rect = scaled.get_rect(center=(cx, cy + y_offset))
    surface.blit(scaled, rect)"""

hypno_aura_blit = """    rect = scaled.get_rect(center=(cx, cy + y_offset))
    surface.blit(scaled, rect)
    if is_hypno and alpha >= 200:
        # 梦幻七彩魅惑光环
        aura_w, aura_h = int(target_w * 0.9), int(target_h * 0.95)
        aura_surf = pygame.Surface((aura_w, aura_h), pygame.SRCALPHA)
        glow_alpha = int(45 + 25 * math.sin(time_value * 6.0))
        pygame.draw.ellipse(aura_surf, (255, 140, 230, glow_alpha), aura_surf.get_rect())
        surface.blit(aura_surf, (cx - aura_w // 2, cy + y_offset - aura_h // 2), special_flags=pygame.BLEND_RGBA_ADD)"""

assert target_blit in graph_code, "target_blit not found in pvz_graphics.py"
graph_code = graph_code.replace(target_blit, hypno_aura_blit, 1)

with open(GRAPH_PY, "w", encoding="utf-8") as f:
    f.write(graph_code)
print("Updated pvz_graphics.py with hypno flips and aura!")

print("\nALL PATCHES APPLIED SUCCESSFULLY!")
