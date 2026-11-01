# -*- coding: utf-8 -*-
"""Apply fixes for:
1. Water plants must be on lilypad (add lilypad for wallnut, add auto-render guard).
2. Match selected_seeds with battlefield plants (so cattail is visibly selected in HUD).
3. Expand slot_capacity to 9 plants (support keys 1-9, HUD layout, seed select).
4. Refine graphics scaling for squash and catapults.
"""

from pathlib import Path
import re

PVZ_FILE = Path(__file__).resolve().parent.parent / "pvz_ten_levels.py"
GFX_FILE = Path(__file__).resolve().parent.parent / "pvz_graphics.py"

def update_pvz():
    text = PVZ_FILE.read_text(encoding="utf-8")

    # 1. Update default slot_capacity to 9
    text = text.replace(
        "self.slot_capacity: int = 8",
        "self.slot_capacity: int = 9"
    )
    text = text.replace(
        'self.slot_capacity = 9 if "master_belt" in self.artifacts else 8',
        'self.slot_capacity = 10 if "master_belt" in self.artifacts else 9'
    )

    # 2. Support hotkeys 1 to 9
    text = text.replace(
        "elif pygame.K_1 <= key <= pygame.K_8:",
        "elif pygame.K_1 <= key <= pygame.K_9:"
    )

    # 3. Update HUD card rendering in _draw_hud to accommodate 9 cards
    old_hud_cards = '''        self.seed_rects = {}
        deck = self.selected_seeds if self.selected_seeds else self.available_plants()[:self.slot_capacity]
        x = 146
        card_w = 78
        gap = 5
        for i, name in enumerate(deck):
            rect = pygame.Rect(x + i * (card_w + gap), 12, card_w, 76)'''

    new_hud_cards = '''        self.seed_rects = {}
        deck = self.selected_seeds if self.selected_seeds else self.available_plants()[:self.slot_capacity]
        x = 146
        card_w = 72
        gap = 4
        for i, name in enumerate(deck):
            rect = pygame.Rect(x + i * (card_w + gap), 12, card_w, 76)'''
    text = text.replace(old_hud_cards, new_hud_cards)

    # 4. In _draw_seed_select, update bank layout for 9 cards
    old_bank_layout = '''        # Top Bar: 出战植物卡槽 (Seed Bank)
        bank_rect = pygame.Rect(260, 12, 680, 84)
        panel(self.screen, bank_rect, (82, 54, 30), (45, 28, 14), radius=10, width=3, shadow=True)

        text(self.screen, "出战卡槽", self.fonts.get(17, True), (255, 235, 140), (bank_rect.x - 16, bank_rect.y + 16), "topright", (40, 30, 20))
        text(self.screen, f"{len(self.selected_seeds)}/{self.slot_capacity} (点击下阵)", self.fonts.get(12), (210, 210, 190), (bank_rect.x - 16, bank_rect.y + 44), "topright")

        slot_w = 70
        slot_h = 70
        slot_gap = 8
        sx0 = bank_rect.x + (bank_rect.width - (self.slot_capacity * (slot_w + slot_gap) - slot_gap)) // 2
        sy0 = bank_rect.y + 7'''

    new_bank_layout = '''        # Top Bar: 出战植物卡槽 (Seed Bank)
        bank_rect = pygame.Rect(230, 12, 740, 84)
        panel(self.screen, bank_rect, (82, 54, 30), (45, 28, 14), radius=10, width=3, shadow=True)

        text(self.screen, "出战卡槽", self.fonts.get(17, True), (255, 235, 140), (bank_rect.x - 16, bank_rect.y + 16), "topright", (40, 30, 20))
        text(self.screen, f"{len(self.selected_seeds)}/{self.slot_capacity} (点击下阵)", self.fonts.get(12), (210, 210, 190), (bank_rect.x - 16, bank_rect.y + 44), "topright")

        slot_w = 66
        slot_h = 70
        slot_gap = 6
        sx0 = bank_rect.x + (bank_rect.width - (self.slot_capacity * (slot_w + slot_gap) - slot_gap)) // 2
        sy0 = bank_rect.y + 7'''
    text = text.replace(old_bank_layout, new_bank_layout)

    # 5. Update prompt text in seed select
    text = text.replace(
        "点击植物卡牌加入出战槽，至多选择 8 种",
        "点击植物卡牌加入出战槽，至多选择 9 种"
    )

    # 6. Fix setup_preview:
    # A) Ensure wallnut in pool is placed ON A LILYPAD! ("lilypad", 4, 3), ("wallnut", 4, 3)
    # B) Set selected_seeds to perfectly match the plants on the battlefield!
    old_preview_pool = '''        if getattr(self, "is_pool", False):
            # 泳池 6 行豪华演示阵容
            demo_plants = [
                ("sunflower", 0, 0), ("sunflower", 0, 1),
                ("lilypad", 0, 2), ("lilypad", 0, 3), ("cattail", 0, 2),
                ("sunflower", 0, 4), ("sunflower", 0, 5),
                ("cabbagepult", 1, 0), ("repeater", 2, 0), ("torchwood", 3, 0), ("wallnut", 5, 0),
                ("melonpult", 1, 1), ("wintermelon", 2, 1), ("garlic", 4, 1),
                ("lilypad", 1, 2), ("kernelpult", 1, 2), ("lilypad", 2, 2), ("repeater", 2, 2),
                ("lilypad", 1, 3), ("cattail", 1, 3), ("lilypad", 2, 3), ("wallnut", 4, 3),
                ("kernelpult", 1, 4), ("torchwood", 3, 4), ("garlic", 4, 4),
                ("cabbagepult", 1, 5), ("snowpea", 2, 5), ("wallnut", 5, 5),
            ]'''

    new_preview_pool = '''        if getattr(self, "is_pool", False):
            # 泳池 6 行豪华演示阵容：顶栏卡槽与场上植物严格一一对应！
            self.selected_seeds = [
                "sunflower", "lilypad", "cattail", "cabbagepult",
                "kernelpult", "torchwood", "garlic", "melonpult", "wallnut"
            ]
            demo_plants = [
                ("sunflower", 0, 0), ("sunflower", 0, 1),
                ("lilypad", 0, 2), ("cattail", 0, 2),
                ("lilypad", 0, 3), ("cattail", 0, 3),
                ("sunflower", 0, 4), ("sunflower", 0, 5),
                ("cabbagepult", 1, 0), ("torchwood", 3, 0), ("wallnut", 5, 0),
                ("melonpult", 1, 1), ("garlic", 4, 1),
                ("lilypad", 1, 2), ("kernelpult", 1, 2),
                # 水面第 4 列坚果严格种在荷叶（睡莲）上！
                ("lilypad", 4, 3), ("wallnut", 4, 3),
                ("kernelpult", 1, 4), ("torchwood", 3, 4), ("garlic", 4, 4),
                ("cabbagepult", 1, 5), ("wallnut", 5, 5),
            ]'''
    text = text.replace(old_preview_pool, new_preview_pool)

    # 7. Add water-lilypad auto-guard in _draw_entities
    old_draw_plants = '''        for plant in sorted(self.plants, key=lambda p: (p.row, 0 if p.ptype == 'lilypad' else 1, p.y)):
            if not plant.alive:
                continue
            draw_plant(
                self.screen, plant.ptype, (plant.x, plant.y), 0.92,
                self.ambient, max(0.0, plant.hp / plant.max_hp), plant.age,
                plant=plant,
            )'''

    new_draw_plants = '''        for plant in sorted(self.plants, key=lambda p: (p.row, 0 if p.ptype == 'lilypad' else 1, p.y)):
            if not plant.alive:
                continue
            # 水面荷叶保障：水面陆生植物必须且必然站在睡莲上
            if getattr(self, "is_pool", False) and plant.row in getattr(self, "pool_rows", ()):
                if plant.ptype not in ("lilypad", "cattail"):
                    has_lily = any(p.alive and p.col == plant.col and p.row == plant.row and p.ptype == "lilypad" for p in self.plants)
                    if not has_lily:
                        draw_plant(self.screen, "lilypad", (plant.x, plant.y), 0.92, self.ambient, 1.0, 10.0)
            draw_plant(
                self.screen, plant.ptype, (plant.x, plant.y), 0.92,
                self.ambient, max(0.0, plant.hp / plant.max_hp), plant.age,
                plant=plant,
            )'''
    text = text.replace(old_draw_plants, new_draw_plants)

    PVZ_FILE.write_text(text, encoding="utf-8")
    print("PVZ_LOGIC_UPDATED")

def update_gfx():
    text = GFX_FILE.read_text(encoding="utf-8")

    # Update plant scaling in render_plant_sprite
    old_p_sizes = '''    elif plant_type in ("cabbagepult", "kernelpult"):
        target_h = int(88 * scale)
        y_offset = 0 * scale
    elif plant_type in ("melonpult", "wintermelon"):
        target_h = int(94 * scale)
        y_offset = -4 * scale'''

    new_p_sizes = '''    elif plant_type == "squash":
        target_h = int(92 * scale)
        y_offset = 4 * scale
    elif plant_type in ("cabbagepult", "kernelpult"):
        target_h = int(92 * scale)
        y_offset = 2 * scale
    elif plant_type in ("melonpult", "wintermelon"):
        target_h = int(96 * scale)
        y_offset = 0 * scale'''

    text = text.replace(old_p_sizes, new_p_sizes)
    GFX_FILE.write_text(text, encoding="utf-8")
    print("GFX_SIZES_UPDATED")

if __name__ == "__main__":
    update_pvz()
    update_gfx()
