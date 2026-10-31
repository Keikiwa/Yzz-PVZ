# -*- coding: utf-8 -*-
"""Generate animation frames and cards for 4 new expansion plants:
- cobcannon (玉米加农炮)
- magicshroom (魔术菇)
- agave (龙舌兰)
- laserbean (激光豆)
"""

import math
from pathlib import Path
from PIL import Image, ImageDraw

ASSETS_DIR = Path(r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz\assets")
PLANTS_DIR = ASSETS_DIR / "plants"
CARDS_DIR = ASSETS_DIR / "cards"

FRAME_COUNT = 12
CANVAS_SIZE = 120

def create_card_base(plant_name: str, plant_img: Image.Image, cost: int) -> Image.Image:
    w, h = 64, 90
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # 经典 PC 浅黄绿色卡牌边框与底纸
    d.rounded_rectangle([1, 1, w - 2, h - 2], radius=6, fill=(245, 236, 196), outline=(92, 104, 76), width=2)
    d.rounded_rectangle([4, 4, w - 5, h - 22], radius=4, fill=(252, 248, 225), outline=(186, 178, 142), width=1)

    # 植物缩放居中绘制
    p_w, p_h = plant_img.size
    scale = min(50 / p_w, 52 / p_h)
    tw, th = int(p_w * scale), int(p_h * scale)
    scaled_p = plant_img.resize((tw, th), Image.Resampling.LANCZOS)
    im.alpha_composite(scaled_p, ((w - tw) // 2, 8 + (54 - th) // 2))

    # 底部深色阳光价格标签栏
    d.rounded_rectangle([3, h - 20, w - 4, h - 3], radius=4, fill=(54, 72, 46))
    
    # 金色小太阳
    d.ellipse([6, h - 17, 18, h - 5], fill=(255, 220, 50), outline=(215, 140, 20), width=1)

    # 阳光数值小方块与数字
    # 留出优雅右侧留白
    return im

def generate_cobcannon_frames():
    """玉米加农炮：重型装甲炮车底座，金黄硕大玉米炮弹，金色能量蓄力"""
    out_dir = PLANTS_DIR / "cobcannon"
    out_dir.mkdir(parents=True, exist_ok=True)
    frames = []

    for f in range(FRAME_COUNT):
        phase = (f / FRAME_COUNT) * 2 * math.pi
        im = Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        cx, cy = 60, 65

        # 呼吸与微震动
        breath = math.sin(phase) * 2.0
        glow = (math.sin(phase * 2) + 1) * 0.5

        # 1. 重型钢铁轮轴与底架
        d.ellipse([cx - 38, cy + 12 + breath, cx - 18, cy + 32 + breath], fill=(85, 95, 90), outline=(45, 55, 50), width=2)
        d.ellipse([cx + 18, cy + 12 + breath, cx + 38, cy + 32 + breath], fill=(85, 95, 90), outline=(45, 55, 50), width=2)
        d.ellipse([cx - 32, cy + 18 + breath, cx - 24, cy + 26 + breath], fill=(160, 175, 170))
        d.ellipse([cx + 24, cy + 18 + breath, cx + 26 + 6, cy + 26 + breath], fill=(160, 175, 170))

        # 绿色加农炮外壳装甲
        d.rounded_rectangle([cx - 40, cy - 8 + breath, cx + 40, cy + 18 + breath], radius=8, fill=(78, 128, 54), outline=(42, 75, 28), width=3)
        # 金属铭牌与固定铆钉
        d.ellipse([cx - 34, cy - 2 + breath, cx - 30, cy + 2 + breath], fill=(225, 205, 120))
        d.ellipse([cx + 30, cy - 2 + breath, cx + 34, cy + 2 + breath], fill=(225, 205, 120))

        # 2. 仰天倾斜的巨型黄金玉米炮弹
        # 弹体外形（圆润饱满）
        cannon_box = [cx - 24, cy - 44 + breath, cx + 26, cy + 8 + breath]
        d.ellipse(cannon_box, fill=(255, 215, 60), outline=(195, 135, 20), width=3)
        # 颗粒饱满的玉米粒网格纹理
        for row in range(5):
            for col in range(4):
                kx = cx - 14 + col * 8
                ky = cy - 36 + row * 8 + breath
                d.ellipse([kx - 2, ky - 2, kx + 3, ky + 3], fill=(255, 235, 110), outline=(215, 160, 30))

        # 3. 炮弹顶端金色高能蓄力粒子光环
        glow_r = int(12 + glow * 5)
        d.ellipse([cx - 2 - glow_r, cy - 46 - glow_r + breath, cx + 2 + glow_r, cy - 46 + glow_r + breath], outline=(255, 255, 150, int(180 * glow)), width=2)

        # 4. 炮车威严黑豆双眼
        d.ellipse([cx - 16, cy + 2 + breath, cx - 10, cy + 10 + breath], fill=(25, 35, 25))
        d.ellipse([cx - 14, cy + 4 + breath, cx - 12, cy + 6 + breath], fill=(255, 255, 255))
        d.ellipse([cx + 10, cy + 2 + breath, cx + 16, cy + 10 + breath], fill=(25, 35, 25))
        d.ellipse([cx + 12, cy + 4 + breath, cx + 14, cy + 6 + breath], fill=(255, 255, 255))

        im.save(out_dir / f"frame_{f:02d}.png")
        frames.append(im)

    # 生成标准卡牌
    card = create_card_base("cobcannon", frames[0], 500)
    card.save(CARDS_DIR / "card_cobcannon.png")
    print("玉米加农炮 (cobcannon) 素材生成完毕！")

def generate_magicshroom_frames():
    """魔术菇：神秘紫色小菇，头戴帅气黑亮绅士高礼帽，手持魔杖，扑克卡牌飞舞"""
    out_dir = PLANTS_DIR / "magicshroom"
    out_dir.mkdir(parents=True, exist_ok=True)
    frames = []

    for f in range(FRAME_COUNT):
        phase = (f / FRAME_COUNT) * 2 * math.pi
        im = Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        cx, cy = 60, 68

        sway = math.sin(phase) * 3.0
        hat_tip = math.cos(phase) * 2.0

        # 1. 身体底座与神秘紫菇菌柄
        d.ellipse([cx - 14, cy + 10, cx + 14, cy + 30], fill=(205, 190, 225), outline=(115, 90, 145), width=2)

        # 2. 灵动自信大眼睛
        d.ellipse([cx - 10, cy + 14, cx - 4, cy + 24], fill=(45, 25, 75))
        d.ellipse([cx - 8, cy + 16, cx - 6, cy + 19], fill=(255, 255, 255))
        d.ellipse([cx + 4, cy + 14, cx + 10, cy + 24], fill=(45, 25, 75))
        d.ellipse([cx + 6, cy + 16, cx + 8, cy + 19], fill=(255, 255, 255))
        # 狡黠魔术微笑
        d.arc([cx - 4, cy + 22, cx + 4, cy + 28], 0, 180, fill=(75, 45, 105), width=2)

        # 3. 紫色魔幻菌盖
        d.ellipse([cx - 26, cy - 8 + sway * 0.5, cx + 26, cy + 14 + sway * 0.5], fill=(138, 72, 192), outline=(78, 35, 115), width=2)
        # 菌盖上的魔幻星辉斑点
        d.ellipse([cx - 16, cy + sway * 0.5, cx - 10, cy + 6 + sway * 0.5], fill=(225, 195, 255))
        d.ellipse([cx + 10, cy + 2 + sway * 0.5, cx + 18, cy + 8 + sway * 0.5], fill=(225, 195, 255))

        # 4. 绅士黑色高礼帽（带红色丝带）
        hx = cx + sway * 0.4
        hy = cy - 28 + hat_tip
        d.ellipse([hx - 22, hy + 18, hx + 22, hy + 26], fill=(35, 30, 42), outline=(15, 10, 20), width=2)
        d.rounded_rectangle([hx - 14, hy - 4, hx + 14, hy + 20], radius=3, fill=(48, 42, 56), outline=(22, 18, 28), width=2)
        # 红色丝带
        d.rectangle([hx - 14, hy + 14, hx + 14, hy + 19], fill=(215, 45, 55))

        # 5. 右手小巧魔杖（顶端金色五角星）
        wx = cx + 24 + sway
        wy = cy + 4
        d.line([(wx - 8, wy + 16), (wx + 10, wy - 8)], fill=(125, 85, 45), width=3)
        # 魔杖顶端金色星芒
        d.ellipse([wx + 8, wy - 10, wx + 14, wy - 4], fill=(255, 225, 75), outline=(215, 140, 20), width=1)

        # 6. 身边浮空旋转的小扑克牌
        card_phase = phase + 1.2
        card_x = cx - 28 + math.sin(card_phase) * 6
        card_y = cy - 10 + math.cos(card_phase) * 6
        d.rounded_rectangle([card_x, card_y, card_x + 10, card_y + 14], radius=2, fill=(255, 255, 255), outline=(180, 40, 40), width=1)
        # 牌面红桃
        d.ellipse([card_x + 3, card_y + 4, card_x + 7, card_y + 8], fill=(225, 35, 45))

        im.save(out_dir / f"frame_{f:02d}.png")
        frames.append(im)

    card = create_card_base("magicshroom", frames[0], 175)
    card.save(CARDS_DIR / "card_magicshroom.png")
    print("魔术菇 (magicshroom) 素材生成完毕！")

def generate_agave_frames():
    """龙舌兰：青翠多肉剑刃，锐利叶尖，锋芒内敛蓄势拔剑"""
    out_dir = PLANTS_DIR / "agave"
    out_dir.mkdir(parents=True, exist_ok=True)
    frames = []

    for f in range(FRAME_COUNT):
        phase = (f / FRAME_COUNT) * 2 * math.pi
        im = Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        cx, cy = 60, 68

        tilt = math.sin(phase) * 2.5
        sword_pulse = (math.sin(phase * 2) + 1) * 0.5

        # 1. 龙舌兰底部多肉叶瓣层叠底座
        d.ellipse([cx - 26, cy + 8, cx + 26, cy + 28], fill=(62, 118, 92), outline=(32, 70, 52), width=2)
        d.polygon([(cx - 28, cy + 18), (cx - 42, cy + 4), (cx - 16, cy + 12)], fill=(75, 138, 108), outline=(35, 75, 58))
        d.polygon([(cx + 28, cy + 18), (cx + 42, cy + 4), (cx + 16, cy + 12)], fill=(75, 138, 108), outline=(35, 75, 58))

        # 2. 沉着坚毅刺客眼神
        d.ellipse([cx - 14, cy + 8, cx - 6, cy + 16], fill=(25, 45, 35))
        d.ellipse([cx - 12, cy + 10, cx - 10, cy + 12], fill=(255, 255, 255))
        d.ellipse([cx + 6, cy + 8, cx + 14, cy + 16], fill=(25, 45, 35))
        d.ellipse([cx + 8, cy + 10, cx + 10, cy + 12], fill=(255, 255, 255))
        # 刀疤般的英武眉线
        d.line([(cx - 16, cy + 6), (cx - 5, cy + 8)], fill=(32, 60, 46), width=2)
        d.line([(cx + 5, cy + 8), (cx + 16, cy + 6)], fill=(32, 60, 46), width=2)

        # 3. 正中央直插云霄的青色巨剑主叶
        blade_top_x = cx + tilt
        blade_top_y = cy - 42 + sword_pulse * 3
        blade = [
            (blade_top_x, blade_top_y),
            (cx + 16, cy + 8),
            (cx, cy + 16),
            (cx - 16, cy + 8),
        ]
        d.polygon(blade, fill=(88, 168, 126), outline=(42, 92, 66), width=2)
        # 剑刃中间高光脊线
        d.line([(blade_top_x, blade_top_y + 4), (cx, cy + 14)], fill=(185, 245, 215), width=2)

        # 4. 剑尖青芒剑气粒子
        aura_r = int(6 + sword_pulse * 4)
        d.ellipse([blade_top_x - aura_r, blade_top_y - aura_r, blade_top_x + aura_r, blade_top_y + aura_r], outline=(150, 255, 210, int(200 * sword_pulse)), width=2)

        im.save(out_dir / f"frame_{f:02d}.png")
        frames.append(im)

    card = create_card_base("agave", frames[0], 150)
    card.save(CARDS_DIR / "card_agave.png")
    print("龙舌兰 (agave) 素材生成完毕！")

def generate_laserbean_frames():
    """激光豆：科幻蓝光双眼，圆润豆荚，随时准备齐射贯通激光"""
    out_dir = PLANTS_DIR / "laserbean"
    out_dir.mkdir(parents=True, exist_ok=True)
    frames = []

    for f in range(FRAME_COUNT):
        phase = (f / FRAME_COUNT) * 2 * math.pi
        im = Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        cx, cy = 60, 66

        bob = math.sin(phase) * 2.0
        eye_pulse = (math.sin(phase * 3) + 1) * 0.5

        # 1. 底叶支撑
        d.ellipse([cx - 24, cy + 16 + bob, cx + 24, cy + 30 + bob], fill=(52, 108, 62), outline=(28, 65, 36), width=2)

        # 2. 豆荚身体（饱满科幻青豆）
        d.ellipse([cx - 26, cy - 22 + bob, cx + 26, cy + 22 + bob], fill=(112, 185, 78), outline=(58, 115, 38), width=3)
        # 头部科幻小天线
        d.line([(cx, cy - 22 + bob), (cx, cy - 36 + bob)], fill=(65, 125, 45), width=3)
        d.ellipse([cx - 4, cy - 42 + bob, cx + 4, cy - 34 + bob], fill=(85, 215, 255), outline=(35, 120, 180), width=1)

        # 3. 核心科技：一对超大湛蓝激光机械义眼
        # 左眼
        d.ellipse([cx - 20, cy - 10 + bob, cx - 4, cy + 8 + bob], fill=(18, 48, 85), outline=(12, 28, 52), width=2)
        d.ellipse([cx - 18, cy - 8 + bob, cx - 6, cy + 6 + bob], fill=(60, 185, 255))
        d.ellipse([cx - 14, cy - 4 + bob, cx - 10, cy + 2 + bob], fill=(225, 250, 255))
        # 右眼
        d.ellipse([cx + 4, cy - 10 + bob, cx + 20, cy + 8 + bob], fill=(18, 48, 85), outline=(12, 28, 52), width=2)
        d.ellipse([cx + 6, cy - 8 + bob, cx + 18, cy + 6 + bob], fill=(60, 185, 255))
        d.ellipse([cx + 10, cy - 4 + bob, cx + 14, cy + 2 + bob], fill=(225, 250, 255))

        # 4. 眼睛聚能蓝光
        if eye_pulse > 0.3:
            d.arc([cx - 18, cy - 8 + bob, cx - 6, cy + 6 + bob], 270, 90, fill=(180, 240, 255), width=2)
            d.arc([cx + 6, cy - 8 + bob, cx + 18, cy + 6 + bob], 270, 90, fill=(180, 240, 255), width=2)

        im.save(out_dir / f"frame_{f:02d}.png")
        frames.append(im)

    card = create_card_base("laserbean", frames[0], 200)
    card.save(CARDS_DIR / "card_laserbean.png")
    print("激光豆 (laserbean) 素材生成完毕！")

if __name__ == "__main__":
    generate_cobcannon_frames()
    generate_magicshroom_frames()
    generate_agave_frames()
    generate_laserbean_frames()
    print("=== 全部 4 种新植物高保真素材生成完毕！ ===")
