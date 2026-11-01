# -*- coding: utf-8 -*-
"""Script to apply gradual unlock, artifact rewards, and 2 new plants (tallnut, gatlingpea)."""

from pathlib import Path
import re

PVZ_FILE = Path(__file__).resolve().parent.parent / "pvz_ten_levels.py"

def update_all():
    text = PVZ_FILE.read_text(encoding="utf-8")

    # 1. Update PLANTS dictionary to add tallnut and gatlingpea
    tallnut_gatling = '''    "tallnut": {
        "name": "高坚果", "cost": 125, "cooldown": 20.0, "hp": 8000,
    },
    "gatlingpea": {
        "name": "机枪射手", "cost": 250, "cooldown": 15.0, "hp": 300,
    },
}'''
    text = text.replace('''    "cattail": {
        "name": "猫尾草", "cost": 225, "cooldown": 15.0, "hp": 300,
    },
}''', '''    "cattail": {
        "name": "猫尾草", "cost": 225, "cooldown": 15.0, "hp": 300,
    },
''' + tallnut_gatling)

    # 2. Update UNLOCK_ORDER
    text = text.replace('''    "melonpult",
    "wintermelon",
]''', '''    "melonpult",
    "wintermelon",
    "tallnut",
    "gatlingpea",
]''')

    # 3. Update PLANT_TIPS
    text = text.replace('''    "cattail": "猫尾草：水生制导王者！种植在睡莲上，可向全图任何一行的僵尸发射自动追踪刺针！",
}''', '''    "cattail": "猫尾草：水生制导王者！种植在睡莲上，可向全图任何一行的僵尸发射自动追踪刺针！",
    "tallnut": "高坚果：拥有 8000 超高血量的重型钢铁壁垒！撑杆跳与海豚僵尸绝对无法跳越！",
    "gatlingpea": "机枪射手：头戴钢盔的终极射手！一次性扫射 4 颗豌豆，配合火炬树桩火力毁天灭地！",
}''')

    # 4. Add LEVEL_REWARDS & ARTIFACT_INFO constants
    rewards_block = '''
LEVEL_REWARDS = {
    0: {"plants": ["wallnut"], "artifact": None},
    1: {"plants": ["snowpea"], "artifact": None},
    2: {"plants": ["potatomine"], "artifact": None},
    3: {"plants": ["repeater"], "artifact": None},
    4: {
        "plants": ["squash"],
        "artifact": "golden_shovel",
        "artifact_name": "黄金阳光铲",
        "artifact_desc": "神奇黄金铁铲！铲除任何植物时，100% 全额返还种植所消耗的阳光！",
    },
    5: {"plants": ["puffshroom", "sunshroom"], "artifact": None},
    6: {"plants": ["spikeweed", "cherrybomb"], "artifact": None},
    7: {
        "plants": ["chomper"],
        "artifact": "sun_vault",
        "artifact_name": "阳光储蓄罐",
        "artifact_desc": "戴夫特制存钱罐！每个关卡开局额外赠送 +100 点初始阳光储备！",
    },
    8: {"plants": ["threepeater", "iceshroom"], "artifact": None},
    9: {
        "plants": ["jalapeno"],
        "artifact": "rapid_seeds",
        "artifact_name": "园艺快手手套",
        "artifact_desc": "熟练园丁的特制手套！全植物种植冷却恢复速度提升 30%！",
    },
    10: {"plants": ["lilypad", "cabbagepult"], "artifact": None},
    11: {
        "plants": ["kernelpult", "torchwood"],
        "artifact": "golden_mower",
        "artifact_name": "镀金清扫车",
        "artifact_desc": "华丽镀金清扫车！当割草机或泳池清扫机被触发碾压时，额外爆落 200 点阳光！",
    },
    12: {"plants": ["garlic", "cattail"], "artifact": None},
    13: {"plants": ["melonpult", "tallnut"], "artifact": None},
    14: {
        "plants": ["wintermelon", "gatlingpea"],
        "artifact": "master_belt",
        "artifact_name": "大师战术腰带",
        "artifact_desc": "顶级战术大师腰带！出战卡槽容量永久扩充至 9 格！",
    },
    15: {"plants": [], "artifact": None},
}

DEFAULT_INITIAL_PLANTS = ["sunflower", "peashooter"]
'''
    if "LEVEL_REWARDS =" not in text:
        text = text.replace("def clamp(", rewards_block + "\ndef clamp(")

    # 5. Update load_save and record_win
    old_save_funcs = '''def load_save() -> dict:
    try:
        if SAVE_FILE.exists():
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {"completed": [], "endless_best": 0}


def record_win(level_idx: int, endless_wave: int = 0) -> None:
    data = load_save()
    if "completed" not in data:
        data["completed"] = []
    if level_idx not in data["completed"]:
        data["completed"].append(level_idx)
    if endless_wave > data.get("endless_best", 0):
        data["endless_best"] = endless_wave
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass'''

    new_save_funcs = '''def load_save() -> dict:
    try:
        if SAVE_FILE.exists():
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {"completed": [], "artifacts": [], "endless_best": 0}


def record_win(level_idx: int, endless_wave: int = 0) -> dict:
    data = load_save()
    if "completed" not in data:
        data["completed"] = []
    if "artifacts" not in data:
        data["artifacts"] = []

    first_time = level_idx not in data["completed"]
    if first_time:
        data["completed"].append(level_idx)

    reward_info = LEVEL_REWARDS.get(level_idx, {})
    new_art = reward_info.get("artifact")
    if new_art and new_art not in data["artifacts"]:
        data["artifacts"].append(new_art)

    if endless_wave > data.get("endless_best", 0):
        data["endless_best"] = endless_wave

    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
    return {"first_time": first_time, "reward": reward_info}'''

    text = text.replace(old_save_funcs, new_save_funcs)

    # 6. Update Game.__init__
    old_game_init = '''        self.is_pool = False
        self.rows = ROWS
        self.cell_h = CELL_H
        self.pool_rows: list[int] = []
        self.grid_bottom = GRID_BOTTOM
        self.clock = pygame.time.Clock()'''

    new_game_init = '''        self.is_pool = False
        self.rows = ROWS
        self.cell_h = CELL_H
        self.pool_rows: list[int] = []
        self.grid_bottom = GRID_BOTTOM
        self.save_data = load_save()
        self.artifacts = set(self.save_data.get("artifacts", []))
        self.slot_capacity = 9 if "master_belt" in self.artifacts else 8
        self.reward_overlay_data: dict | None = None
        self.clock = pygame.time.Clock()'''

    text = text.replace(old_game_init, new_game_init)

    # 7. Update available_plants to respect gradual unlocking
    old_avail_plants = '''    def available_plants(self) -> list[str]:
        # Unlock plants dynamically with level index
        unlock_count = min(len(UNLOCK_ORDER), max(4, self.level_index + 4))
        if self.level_index >= 10:
            unlock_count = len(UNLOCK_ORDER)
        return UNLOCK_ORDER[:unlock_count]'''

    new_avail_plants = '''    def available_plants(self) -> list[str]:
        # 植物逐步赠送解锁系统：第一关仅基础植物，随后每通关一关解锁赠送新植物
        save = load_save()
        completed = set(save.get("completed", []))
        unlocked = list(DEFAULT_INITIAL_PLANTS)
        for c_idx in sorted(completed):
            rewards = LEVEL_REWARDS.get(c_idx, {}).get("plants", [])
            for p in rewards:
                if p in UNLOCK_ORDER and p not in unlocked:
                    unlocked.append(p)

        # 当前关卡本身需要具备的基础出战植物保障
        # 如果是在测试模式或关卡大于已通关很多，给予到该关卡为止的默认解锁
        min_allowed = min(len(UNLOCK_ORDER), max(len(unlocked), self.level_index + 2))
        for p in UNLOCK_ORDER[:min_allowed]:
            if p not in unlocked:
                unlocked.append(p)

        # 泳池关卡（11关及以后）必须自动获得睡莲作为水生载体
        if getattr(self, "is_pool", False) and "lilypad" not in unlocked:
            unlocked.append("lilypad")

        return [p for p in UNLOCK_ORDER if p in unlocked]'''

    text = text.replace(old_avail_plants, new_avail_plants)

    # 8. Update start_level
    old_start_level = '''        self.is_pool = bool(level.get("pool", False))
        self.rows = 6 if self.is_pool else 5
        self.cell_h = 96 if self.is_pool else 116
        self.pool_rows = [2, 3] if self.is_pool else []
        self.grid_bottom = GRID_Y + self.rows * self.cell_h
        self._reset_runtime()
        self.sun = level["sun"]'''

    new_start_level = '''        self.is_pool = bool(level.get("pool", False))
        self.rows = 6 if self.is_pool else 5
        self.cell_h = 96 if self.is_pool else 116
        self.pool_rows = [2, 3] if self.is_pool else []
        self.grid_bottom = GRID_Y + self.rows * self.cell_h
        self.save_data = load_save()
        self.artifacts = set(self.save_data.get("artifacts", []))
        self.slot_capacity = 9 if "master_belt" in self.artifacts else 8
        self._reset_runtime()
        bonus_sun = 100 if "sun_vault" in self.artifacts else 0
        self.sun = level["sun"] + bonus_sun'''

    text = text.replace(old_start_level, new_start_level)

    # 9. Update _try_plant for golden shovel refund & rapid seeds cooldown
    old_shovel_part = '''        if self.shovel_selected:
            if top_plant is not None:
                top_plant.alive = False
                self.burst(top_plant.x, top_plant.y, (141, 98, 54), 15)
                self.float_text(top_plant.x, top_plant.y - 30, "已移除", C_CREAM)
            self.shovel_selected = False
            return'''

    new_shovel_part = '''        if self.shovel_selected:
            if top_plant is not None:
                cost = PLANTS[top_plant.ptype]["cost"]
                has_gold = "golden_shovel" in self.artifacts
                top_plant.alive = False
                self.burst(top_plant.x, top_plant.y, (255, 215, 80) if has_gold else (141, 98, 54), 16)
                if has_gold:
                    self.sun += cost
                    self.float_text(top_plant.x, top_plant.y - 30, f"+{cost} 黄金阳光返还！", C_GOLD)
                    self.audio.play("collect")
                else:
                    self.float_text(top_plant.x, top_plant.y - 30, "已移除", C_CREAM)
            self.shovel_selected = False
            return'''

    text = text.replace(old_shovel_part, new_shovel_part)

    # 10. Update cooldown reduction in _try_plant
    old_cd_apply = '''        self.sun -= cost
        self.cooldowns[name] = PLANTS[name]["cooldown"]'''
    new_cd_apply = '''        self.sun -= cost
        cd_mult = 0.70 if "rapid_seeds" in self.artifacts else 1.0
        self.cooldowns[name] = PLANTS[name]["cooldown"] * cd_mult'''
    text = text.replace(old_cd_apply, new_cd_apply)

    # 11. Update Mower update for golden_mower bonus
    old_mower_update = '''        if not self.triggered:
            return
        self.x += 520 * dt
        for zombie in game.zombies:
            if zombie.row == self.row and not zombie.dead and abs(zombie.x - self.x) < 62:
                game.kill_zombie(zombie, mower=True)
        if self.x > WIDTH + 60:
            self.spent = True'''

    new_mower_update = '''        if not self.triggered:
            return
        if not getattr(self, "rewarded_gold", False) and "golden_mower" in game.artifacts:
            self.rewarded_gold = True
            game.sun += 200
            game.float_text(self.x + 30, lane_ground(self.row, cell_h=self.cell_h) - 40, "+200 镀金奖励！", C_GOLD)
            game.burst(self.x + 30, lane_ground(self.row, cell_h=self.cell_h) - 20, (255, 220, 80), 20)
            game.audio.play("collect")
        self.x += 520 * dt
        for zombie in game.zombies:
            if zombie.row == self.row and not zombie.dead and abs(zombie.x - self.x) < 62:
                game.kill_zombie(zombie, mower=True)
        if self.x > WIDTH + 60:
            self.spent = True'''

    text = text.replace(old_mower_update, new_mower_update)

    # 12. Update _update_zombies for tallnut blocking vault and jumping
    old_pole_vault = '''                if zombie.vault_state == "run":
                    target_plant = self._plant_under_attack(zombie, plants_by_row)
                    if target_plant and target_plant.alive:
                        zombie.vault_state = "jumping"
                        zombie.vault_progress = 0.0
                        zombie.eating = 0.0
                        self.audio.play("vault")'''

    new_pole_vault = '''                if zombie.vault_state == "run":
                    target_plant = self._plant_under_attack(zombie, plants_by_row)
                    if target_plant and target_plant.alive:
                        if target_plant.ptype == "tallnut":
                            # 高坚果拦截撑杆跳！
                            zombie.has_pole = False
                            zombie.vault_state = "done"
                            zombie.speed = 16.0
                            self.audio.play("groan")
                            self.float_text(zombie.x, zombie.y - 30, "撞上高坚果！", (255, 120, 100))
                            self.burst(zombie.x, zombie.y, (180, 140, 90), 12)
                        else:
                            zombie.vault_state = "jumping"
                            zombie.vault_progress = 0.0
                            zombie.eating = 0.0
                            self.audio.play("vault")'''
    text = text.replace(old_pole_vault, new_pole_vault)

    old_dolphin_vault = '''                if zombie.vault_state == "run":
                    target_plant = self._plant_under_attack(zombie, plants_by_row)
                    if target_plant and target_plant.alive:
                        zombie.vault_state = "jumping"
                        zombie.vault_progress = 0.0
                        zombie.eating = 0.0
                        self.audio.play("vault")
                        self.audio.play("splash", cooldown=0.3)'''

    new_dolphin_vault = '''                if zombie.vault_state == "run":
                    target_plant = self._plant_under_attack(zombie, plants_by_row)
                    if target_plant and target_plant.alive:
                        if target_plant.ptype == "tallnut":
                            # 高坚果拦截海豚飞跃！
                            zombie.has_dolphin = False
                            zombie.vault_state = "done"
                            zombie.speed = 16.0
                            self.audio.play("splash", cooldown=0.3)
                            self.float_text(zombie.x, zombie.y - 30, "高坚果封锁水域！", (255, 120, 100))
                            self.burst(zombie.x, zombie.y, (120, 220, 255), 18)
                        else:
                            zombie.vault_state = "jumping"
                            zombie.vault_progress = 0.0
                            zombie.eating = 0.0
                            self.audio.play("vault")
                            self.audio.play("splash", cooldown=0.3)'''
    text = text.replace(old_dolphin_vault, new_dolphin_vault)

    # 13. Update _update_plants for gatlingpea
    old_cabbage_update = '''            elif plant.ptype == "cabbagepult":'''
    gatling_update = '''            elif plant.ptype == "gatlingpea":
                if plant.action_timer >= 1.45:
                    has_target = any(
                        z.row == plant.row and not z.dead and z.x > plant.x - 20 and z.x < GRID_RIGHT + 180
                        for z in self.zombies
                    )
                    if has_target:
                        plant.action_timer = 0
                        y = lane_ground(plant.row, cell_h=self.cell_h) - 70
                        # 四连发强力机枪扫射
                        for b_i in range(4):
                            self.projectiles.append(Projectile(plant.x + 24 - b_i * 12, y + (b_i % 2) * 4, plant.row, 25))
                        self.audio.play("plant", cooldown=0.1)
            elif plant.ptype == "cabbagepult":'''
    text = text.replace(old_cabbage_update, gatling_update)

    # 14. Update _check_progress to record victory and prepare rewards overlay
    old_check_prog = '''        if not self.pending_wave_spawns and not any(not z.dead for z in self.zombies):
            self.overlay = "won"
            record_win(self.level_index)
            self.audio.stop_music()
            self.audio.play("win")'''

    new_check_prog = '''        if not self.pending_wave_spawns and not any(not z.dead for z in self.zombies):
            self.overlay = "won"
            res = record_win(self.level_index)
            self.save_data = load_save()
            self.artifacts = set(self.save_data.get("artifacts", []))
            self.reward_overlay_data = res
            self.audio.stop_music()
            self.audio.play("win")'''
    text = text.replace(old_check_prog, new_check_prog)

    # 15. Update _draw_overlays to draw reward showcase
    old_won_overlay = '''        elif self.overlay == "won":
            text(self.screen, "草坪全线告捷！", self.fonts.get(44, True), (255, 235, 120), (WIDTH // 2, 232), "center", (45, 62, 35))
            text(
                self.screen, f"恭喜通过第 {self.level_index + 1} 关 · {level['name']}",
                self.fonts.get(22, True), C_CREAM, (WIDTH // 2, 290), "center",
            )
            text(
                self.screen, f"成功消灭所有波次尸群 · 守卫了向日葵与戴夫的房屋！",
                self.fonts.get(16), (220, 240, 205), (WIDTH // 2, 335), "center",
            )'''

    new_won_overlay = '''        elif self.overlay == "won":
            rew_info = LEVEL_REWARDS.get(self.level_index, {})
            rew_plants = rew_info.get("plants", [])
            rew_art = rew_info.get("artifact")

            text(self.screen, "🎉 关卡全线大捷！", self.fonts.get(42, True), (255, 235, 120), (WIDTH // 2, 175), "center", (45, 62, 35))
            text(
                self.screen, f"恭喜通过第 {self.level_index + 1} 关 · {level['name']}",
                self.fonts.get(20, True), C_CREAM, (WIDTH // 2, 222), "center",
            )

            # 奖励展示区域
            card_box = pygame.Rect(320, 260, 560, 230)
            panel(self.screen, card_box, (246, 236, 204), (88, 64, 38), radius=12, width=3, shadow=True)
            text(self.screen, "【 通 关 奖 励 结 算 】", self.fonts.get(15, True), (120, 80, 40), (card_box.centerx, card_box.y + 12), "midtop")

            if rew_art:
                art_name = rew_info.get("artifact_name", "通关专属神器")
                art_desc = rew_info.get("artifact_desc", "")
                art_badge = pygame.Rect(card_box.x + 24, card_box.y + 40, 90, 80)
                panel(self.screen, art_badge, (255, 215, 80), (145, 105, 30), radius=10, width=3)
                text(self.screen, "👑", self.fonts.get(34), (45, 30, 15), (art_badge.centerx, art_badge.centery - 6), "center")
                text(self.screen, "神器", self.fonts.get(11, True), (95, 65, 20), (art_badge.centerx, art_badge.bottom - 14), "center")

                text(self.screen, f"解锁专属神器：{art_name}", self.fonts.get(18, True), (160, 70, 20), (card_box.x + 130, card_box.y + 45))
                text(self.screen, art_desc, self.fonts.get(13), (90, 70, 50), (card_box.x + 130, card_box.y + 75))
            elif rew_plants:
                p_names = "、".join([PLANTS[p]["name"] for p in rew_plants])
                p_desc = "  ".join([PLANT_TIPS.get(p, "") for p in rew_plants])
                # 展示获得植物卡牌
                for p_idx, p in enumerate(rew_plants[:2]):
                    c_rect = pygame.Rect(card_box.x + 30 + p_idx * 90, card_box.y + 42, 76, 76)
                    c_surf = pvz_graphics.get_card_surface(p, (76, 76))
                    if c_surf:
                        self.screen.blit(c_surf, c_rect)
                    else:
                        panel(self.screen, c_rect, (255, 245, 215), (80, 80, 60), radius=6, width=2)
                        draw_plant(self.screen, p, (c_rect.centerx, c_rect.y + 36), 0.35, self.time_value)
                text(self.screen, f"获得新植物：{p_names}", self.fonts.get(18, True), (42, 110, 48), (card_box.x + 210 if len(rew_plants) > 1 else card_box.x + 125, card_box.y + 45))
                text(self.screen, p_desc[:65] + ("..." if len(p_desc) > 65 else ""), self.fonts.get(12), (85, 75, 55), (card_box.x + 210 if len(rew_plants) > 1 else card_box.x + 125, card_box.y + 75))
            else:
                text(self.screen, "恭喜坚守到底！你的草坪与泳池防线固若金汤！", self.fonts.get(16, True), (55, 85, 50), (card_box.centerx, card_box.y + 60), "center")

            # 底部小字
            unlocked_total = len(self.available_plants())
            text(
                self.screen, f"已累计解锁 {unlocked_total} 种植物  ·  已激活 {len(self.artifacts)} 件通关专属神器",
                self.fonts.get(13, True), (135, 100, 55), (card_box.centerx, card_box.bottom - 22), "center",
            )'''

    text = text.replace(old_won_overlay, new_won_overlay)

    # 16. Update HUD to draw Gold Shovel visual indicator
    old_shovel_draw = '''        shovel_box = pygame.Rect(1092, 49, 45, 36)'''
    new_shovel_draw = '''        shovel_box = pygame.Rect(1092, 49, 45, 36)
        if "golden_shovel" in getattr(self, "artifacts", ()):
            # 黄金阳光铲金色耀光外框
            pygame.draw.rect(self.screen, (255, 215, 60), shovel_box.inflate(4, 4), 2, border_radius=9)
            draw_glow_circle(self.screen, (shovel_box.centerx, shovel_box.centery), 12, (255, 230, 90))'''
    text = text.replace(old_shovel_draw, new_shovel_draw)

    PVZ_FILE.write_text(text, encoding="utf-8")
    print("All rewards, gradual unlock, and extra plants successfully integrated.")

if __name__ == "__main__":
    update_all()
