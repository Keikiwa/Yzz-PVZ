# -*- coding: utf-8 -*-
"""Fix cattail spike residual bug and add intelligent retargeting & angle rotation."""

from pathlib import Path

pvz_main_path = Path("10-pvz/pvz_ten_levels.py")
with open(pvz_main_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update Projectile class: add angle & age, update() receives game parameter for retargeting
old_proj_update = '''    def update(self, dt: float) -> None:
        if self.is_homing:
            if self.target_zombie and not getattr(self.target_zombie, "dead", True):
                tx = getattr(self.target_zombie, "x", self.x)
                ty = getattr(self.target_zombie, "y", self.y)
                dx = tx - self.x
                dy = ty - self.y
                dist = math.hypot(dx, dy)
                if dist > 0.01:
                    step = min(dist, self.speed * dt)
                    self.x += (dx / dist) * step
                    self.y += (dy / dist) * step
                if dist < 24.0:
                    self.lob_progress = 1.0
        elif self.is_lobbed:
            self.lob_progress += dt / max(0.001, self.lob_duration)
            p = min(1.0, self.lob_progress)
            if self.target_zombie and not getattr(self.target_zombie, "dead", True):
                self.target_x = getattr(self.target_zombie, "x", self.target_x)
            self.x = self.start_x + (self.target_x - self.start_x) * p
            linear_y = self.start_y + (self.target_y - self.start_y) * p
            arc = 4.0 * self.apex_h * p * (1.0 - p)
            self.y = linear_y - arc
        else:
            self.x += self.speed * dt
        if self.x > WIDTH + 80 or self.x < -80 or self.y < -80 or self.y > HEIGHT + 80:
            self.alive = False'''

new_proj_update = '''    angle: float = 0.0
    age: float = 0.0

    def update(self, dt: float, game: object = None) -> None:
        self.age = getattr(self, "age", 0.0) + dt
        if self.is_homing:
            # 存活时间保护防残留兜底 (超过 4.5 秒自动消散)
            if self.age > 4.5:
                self.alive = False
                return

            target = self.target_zombie
            # 若原目标已死或脱离屏幕，自动重选全场存活新目标！
            if not target or getattr(target, "dead", True) or getattr(target, "x", 0) > WIDTH + 100:
                if game and hasattr(game, "zombies"):
                    alive_z = [z for z in game.zombies if not z.dead and not getattr(z, "hypnotized", False) and z.x < WIDTH + 80]
                    if alive_z:
                        # 优先追踪气球僵尸，其次追踪最靠前的僵尸
                        balloon_z = [z for z in alive_z if getattr(z, "ztype", "") == "balloon" and getattr(z, "flying", True)]
                        target = balloon_z[0] if balloon_z else min(alive_z, key=lambda z: z.x)
                        self.target_zombie = target
                    else:
                        target = None
                        self.target_zombie = None

            if target and not getattr(target, "dead", True):
                tx = getattr(target, "x", self.x)
                ty = getattr(target, "y", self.y)
                dx = tx - self.x
                dy = ty - self.y
                dist = math.hypot(dx, dy)
                if dist > 0.01:
                    step = min(dist, self.speed * dt)
                    self.x += (dx / dist) * step
                    self.y += (dy / dist) * step
                    self.angle = -math.degrees(math.atan2(dy, dx))
            else:
                # 场上无目标时，刺针沿当前角度朝右前方疾飞出屏幕，绝不残留！
                rad = -math.radians(getattr(self, "angle", 0.0))
                vx = math.cos(rad) * self.speed if rad != 0 else self.speed
                vy = math.sin(rad) * self.speed if rad != 0 else 0.0
                self.x += vx * dt
                self.y += vy * dt
        elif self.is_lobbed:
            self.lob_progress += dt / max(0.001, self.lob_duration)
            p = min(1.0, self.lob_progress)
            if self.target_zombie and not getattr(self.target_zombie, "dead", True):
                self.target_x = getattr(self.target_zombie, "x", self.target_x)
            self.x = self.start_x + (self.target_x - self.start_x) * p
            linear_y = self.start_y + (self.target_y - self.start_y) * p
            arc = 4.0 * self.apex_h * p * (1.0 - p)
            self.y = linear_y - arc
        else:
            self.x += self.speed * dt
        if self.x > WIDTH + 80 or self.x < -80 or self.y < -80 or self.y > HEIGHT + 80:
            self.alive = False'''

assert old_proj_update in code, "old_proj_update not found"
code = code.replace(old_proj_update, new_proj_update, 1)

# 2. Update projectile update call: pass self (game)
old_call = '''            else:
                projectile.update(dt)'''

new_call = '''            else:
                projectile.update(dt, self)'''

assert old_call in code, "old_call not found"
code = code.replace(old_call, new_call, 1)

# 3. Update collision check for homing projectile: distance & spike burst effect
old_hit = '''                if projectile.is_homing:
                    if abs(zombie.x - projectile.x) > 28 or abs(zombie.y - projectile.y) > 36:
                        continue'''

new_hit = '''                if projectile.is_homing:
                    if abs(zombie.x - projectile.x) > 35 or abs(zombie.y - projectile.y) > 42:
                        continue'''

assert old_hit in code, "old_hit not found"
code = code.replace(old_hit, new_hit, 1)

# Spike burst effect when spike hits zombie
old_damage = '''                self._damage_zombie(zombie, projectile.damage, freeze=projectile.freeze)
                break'''

new_damage = '''                if projectile.bullet_type == "cattail_spike":
                    self.burst(projectile.x, projectile.y, (245, 120, 180), 6, speed=120.0)
                self._damage_zombie(zombie, projectile.damage, freeze=projectile.freeze)
                break'''

assert old_damage in code, "old_damage not found"
code = code.replace(old_damage, new_damage, 1)

# 4. Spike rendering with rotation
old_render = '''        for projectile in self.projectiles:
            bullet_surf = pvz_graphics.get_bullet_surface(projectile.freeze, 22, bullet_type=projectile.bullet_type)
            if bullet_surf:
                if projectile.freeze:
                    draw_glow_circle(self.screen, (projectile.x, projectile.y), 7, (125, 225, 246))
                self.screen.blit(bullet_surf, bullet_surf.get_rect(center=(projectile.x, projectile.y)))'''

new_render = '''        for projectile in self.projectiles:
            bullet_surf = pvz_graphics.get_bullet_surface(projectile.freeze, 22, bullet_type=projectile.bullet_type)
            if bullet_surf:
                if projectile.bullet_type == "cattail_spike" and getattr(projectile, "angle", 0.0) != 0.0:
                    bullet_surf = pygame.transform.rotate(bullet_surf, projectile.angle)
                if projectile.freeze:
                    draw_glow_circle(self.screen, (projectile.x, projectile.y), 7, (125, 225, 246))
                self.screen.blit(bullet_surf, bullet_surf.get_rect(center=(projectile.x, projectile.y)))'''

assert old_render in code, "old_render not found"
code = code.replace(old_render, new_render, 1)

with open(pvz_main_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Cattail spike retargeting and residual bug fixed successfully!")
