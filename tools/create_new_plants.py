# -*- coding: utf-8 -*-
"""Generate high-res procedural sprites and seed cards for 5 new plants."""

import math
from pathlib import Path
from PIL import Image, ImageDraw

ASSETS_DIR = Path("10-pvz/assets")
PLANTS_DIR = ASSETS_DIR / "plants"
CARDS_DIR = ASSETS_DIR / "cards"

def create_cards_and_sprites():
    card_template = Image.open(CARDS_DIR / "card_wallnut.png").convert("RGBA")
    
    # -------------------------------------------------------------
    # 1. 魅惑菇 (hypnoshroom) - Cost 75
    # -------------------------------------------------------------
    hypno_dir = PLANTS_DIR / "hypnoshroom"
    hypno_dir.mkdir(parents=True, exist_ok=True)
    for frame_idx in range(12):
        im = Image.new("RGBA", (80, 80), (0, 0, 0, 0))
        draw = ImageDraw.Draw(im)
        t = frame_idx / 12.0 * math.tau
        sway = math.sin(t) * 3
        # Stem
        draw.ellipse([34 + sway*0.3, 45, 46 + sway*0.3, 72], fill=(220, 190, 240, 255), outline=(130, 80, 170, 255), width=2)
        # Cap: Psychedelic pink/purple
        cx, cy = 40 + sway, 36
        draw.ellipse([cx - 28, cy - 22, cx + 28, cy + 18], fill=(225, 75, 185, 255), outline=(110, 20, 90, 255), width=2)
        # Swirling spots
        for i in range(4):
            ang = t + i * math.tau / 4
            sx = cx + math.cos(ang) * 14
            sy = cy + math.sin(ang) * 9
            draw.circle((sx, sy), 5, fill=(255, 220, 100, 255))
        # Eyes
        draw.ellipse([cx - 10, cy - 2, cx - 4, cy + 6], fill=(50, 10, 50, 255))
        draw.ellipse([cx + 4, cy - 2, cx + 10, cy + 6], fill=(50, 10, 50, 255))
        im.save(hypno_dir / f"idle_{frame_idx}.png")
        
    # Card
    card_hypno = card_template.copy()
    draw_c = ImageDraw.Draw(card_hypno)
    draw_c.rectangle([6, 6, 58, 64], fill=(91, 160, 119, 255))
    h_spr = Image.open(hypno_dir / "idle_0.png").resize((44, 44), Image.Resampling.LANCZOS)
    card_hypno.paste(h_spr, ((64 - 44) // 2, 14), h_spr)
    draw_c.rectangle([24, 68, 60, 88], fill=(255, 255, 255, 255))
    draw_c.text((32, 70), "75", fill=(0, 0, 0, 255))
    card_hypno.save(CARDS_DIR / "card_hypnoshroom.png")

    # -------------------------------------------------------------
    # 2. 大喷菇 (fumeshroom) - Cost 75
    # -------------------------------------------------------------
    fume_dir = PLANTS_DIR / "fumeshroom"
    fume_dir.mkdir(parents=True, exist_ok=True)
    for frame_idx in range(12):
        im = Image.new("RGBA", (84, 84), (0, 0, 0, 0))
        draw = ImageDraw.Draw(im)
        t = frame_idx / 12.0 * math.tau
        puff = math.sin(t) * 2
        # Stem
        draw.ellipse([34, 48, 50, 76], fill=(135, 80, 160, 255), outline=(75, 30, 100, 255), width=2)
        # Big snout / head
        draw.ellipse([20, 24, 64 + puff, 56], fill=(160, 95, 195, 255), outline=(75, 30, 100, 255), width=2)
        # Snout opening
        draw.ellipse([58 + puff, 30, 72 + puff, 50], fill=(95, 40, 125, 255), outline=(60, 20, 85, 255), width=2)
        # Eyes
        draw.ellipse([32, 34, 38, 44], fill=(255, 255, 255, 255))
        draw.ellipse([35, 37, 38, 42], fill=(20, 10, 30, 255))
        draw.ellipse([44, 34, 50, 44], fill=(255, 255, 255, 255))
        draw.ellipse([47, 37, 50, 42], fill=(20, 10, 30, 255))
        im.save(fume_dir / f"idle_{frame_idx}.png")
        
    card_fume = card_template.copy()
    draw_c = ImageDraw.Draw(card_fume)
    draw_c.rectangle([6, 6, 58, 64], fill=(91, 160, 119, 255))
    f_spr = Image.open(fume_dir / "idle_0.png").resize((44, 44), Image.Resampling.LANCZOS)
    card_fume.paste(f_spr, ((64 - 44) // 2, 14), f_spr)
    draw_c.rectangle([24, 68, 60, 88], fill=(255, 255, 255, 255))
    draw_c.text((32, 70), "75", fill=(0, 0, 0, 255))
    card_fume.save(CARDS_DIR / "card_fumeshroom.png")

    # -------------------------------------------------------------
    # 3. 毁灭菇 (doomshroom) - Cost 125
    # -------------------------------------------------------------
    doom_dir = PLANTS_DIR / "doomshroom"
    doom_dir.mkdir(parents=True, exist_ok=True)
    for frame_idx in range(12):
        im = Image.new("RGBA", (84, 84), (0, 0, 0, 0))
        draw = ImageDraw.Draw(im)
        t = frame_idx / 12.0 * math.tau
        grow = math.sin(t) * 2
        # Massive black/crimson cap
        draw.ellipse([14 - grow, 18 - grow, 70 + grow, 62 + grow], fill=(42, 32, 48, 255), outline=(18, 12, 24, 255), width=3)
        # Red angry eyes
        draw.ellipse([28, 38, 38, 48], fill=(225, 40, 30, 255))
        draw.ellipse([32, 41, 37, 46], fill=(255, 220, 50, 255))
        draw.ellipse([46, 38, 56, 48], fill=(225, 40, 30, 255))
        draw.ellipse([47, 41, 52, 46], fill=(255, 220, 50, 255))
        # Evil eyebrows
        draw.line([26, 36, 40, 42], fill=(18, 12, 24, 255), width=2)
        draw.line([58, 36, 44, 42], fill=(18, 12, 24, 255), width=2)
        # Stem
        draw.ellipse([30, 56, 54, 76], fill=(30, 22, 36, 255), outline=(18, 12, 24, 255), width=2)
        im.save(doom_dir / f"idle_{frame_idx}.png")
        
    card_doom = card_template.copy()
    draw_c = ImageDraw.Draw(card_doom)
    draw_c.rectangle([6, 6, 58, 64], fill=(91, 160, 119, 255))
    d_spr = Image.open(doom_dir / "idle_0.png").resize((44, 44), Image.Resampling.LANCZOS)
    card_doom.paste(d_spr, ((64 - 44) // 2, 14), d_spr)
    draw_c.rectangle([24, 68, 60, 88], fill=(255, 255, 255, 255))
    draw_c.text((26, 70), "125", fill=(0, 0, 0, 255))
    card_doom.save(CARDS_DIR / "card_doomshroom.png")

    # -------------------------------------------------------------
    # 4. 双子向日葵 (twinsunflower) - Cost 150
    # -------------------------------------------------------------
    twin_dir = PLANTS_DIR / "twinsunflower"
    twin_dir.mkdir(parents=True, exist_ok=True)
    sf_base = Image.open(PLANTS_DIR / "sunflower" / "idle_0.png").convert("RGBA")
    for frame_idx in range(12):
        im = Image.new("RGBA", (110, 84), (0, 0, 0, 0))
        t = frame_idx / 12.0 * math.tau
        sway1 = math.sin(t) * 3
        sway2 = math.cos(t) * 3
        # Left sunflower head (scaled 0.72)
        h1 = sf_base.resize((56, 58), Image.Resampling.LANCZOS)
        # Right sunflower head (scaled 0.72)
        h2 = sf_base.resize((56, 58), Image.Resampling.LANCZOS)
        im.paste(h1, (int(6 + sway1), int(16 + abs(sway1))), h1)
        im.paste(h2, (int(48 + sway2), int(14 + abs(sway2))), h2)
        im.save(twin_dir / f"idle_{frame_idx}.png")

    card_twin = card_template.copy()
    draw_c = ImageDraw.Draw(card_twin)
    draw_c.rectangle([6, 6, 58, 64], fill=(91, 160, 119, 255))
    tw_spr = Image.open(twin_dir / "idle_0.png").resize((50, 38), Image.Resampling.LANCZOS)
    card_twin.paste(tw_spr, ((64 - 50) // 2, 18), tw_spr)
    draw_c.rectangle([24, 68, 60, 88], fill=(255, 255, 255, 255))
    draw_c.text((26, 70), "150", fill=(0, 0, 0, 255))
    card_twin.save(CARDS_DIR / "card_twinsunflower.png")

    # -------------------------------------------------------------
    # 5. 杨桃 / 星星果 (starfruit) - Cost 125
    # -------------------------------------------------------------
    star_dir = PLANTS_DIR / "starfruit"
    star_dir.mkdir(parents=True, exist_ok=True)
    for frame_idx in range(12):
        im = Image.new("RGBA", (80, 80), (0, 0, 0, 0))
        draw = ImageDraw.Draw(im)
        t = frame_idx / 12.0 * math.tau
        rot = math.sin(t) * 0.15
        cx, cy = 40, 40
        # Compute 5 points of a star
        pts = []
        for i in range(10):
            r = 32 if i % 2 == 0 else 14
            ang = rot + i * math.pi / 5 - math.pi / 2
            pts.append((cx + math.cos(ang) * r, cy + math.sin(ang) * r))
        draw.polygon(pts, fill=(255, 225, 45, 255), outline=(210, 165, 20, 255))
        # Eyes
        draw.ellipse([cx - 8, cy - 6, cx - 3, cy + 4], fill=(30, 80, 180, 255))
        draw.ellipse([cx + 3, cy - 6, cx + 8, cy + 4], fill=(30, 80, 180, 255))
        # Smile
        draw.arc([cx - 7, cy, cx + 7, cy + 10], 0, 180, fill=(180, 90, 10, 255), width=2)
        im.save(star_dir / f"idle_{frame_idx}.png")
        
    card_star = card_template.copy()
    draw_c = ImageDraw.Draw(card_star)
    draw_c.rectangle([6, 6, 58, 64], fill=(91, 160, 119, 255))
    st_spr = Image.open(star_dir / "idle_0.png").resize((44, 44), Image.Resampling.LANCZOS)
    card_star.paste(st_spr, ((64 - 44) // 2, 14), st_spr)
    draw_c.rectangle([24, 68, 60, 88], fill=(255, 255, 255, 255))
    draw_c.text((26, 70), "125", fill=(0, 0, 0, 255))
    card_star.save(CARDS_DIR / "card_starfruit.png")

    print("ALL_5_NEW_PLANTS_AND_CARDS_CREATED_SUCCESSFULLY")

if __name__ == "__main__":
    create_cards_and_sprites()
