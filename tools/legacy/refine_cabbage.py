# -*- coding: utf-8 -*-
from PIL import Image
from pathlib import Path

def process_cabbage_and_wintermelon():
    for name, (min_x, max_x, min_y, max_y) in [
        ("cabbagepult", (40, 142, 16, 130)),
        ("wintermelon", (40, 142, 16, 130)),
    ]:
        p_dir = Path(f"10-pvz/assets/plants/{name}")
        files = list(p_dir.glob("*.png"))
        print(f"Refining {name}: {len(files)} frames...")
        for f in files:
            im = Image.open(f).convert("RGBA")
            # 裁剪植物主体区域
            crop_im = im.crop((min_x, min_y, max_x, max_y))
            # 清理边缘残留噪点
            pix = crop_im.load()
            cw, ch = crop_im.size
            for cx in range(cw):
                for cy in range(ch):
                    r, g, b, a = pix[cx, cy]
                    # 如果是暗草绿或者土黄背景
                    if (g > 35 and g > r and g > b and b < 50) or (r > 60 and g > 50 and b < 25 and r < 120 and g < 100):
                        # 判断是否不是卷心菜或投石机
                        is_plant = (g > 165 and g > r * 1.15) or (r > 130 and g > 90) or (b > 150)
                        if not is_plant:
                            pix[cx, cy] = (0, 0, 0, 0)
            crop_im.save(f)
            
    print("REFINING_DONE")

if __name__ == "__main__":
    process_cabbage_and_wintermelon()
