# -*- coding: utf-8 -*-
import urllib.request
import re

plants = [
    ("fumeshroom", "Fume-shroom"),
    ("hypnoshroom", "Hypno-shroom"),
    ("doomshroom", "Doom-shroom"),
    ("cattail", "Cattail"),
    ("twinsunflower", "Twin_Sunflower"),
    ("starfruit", "Starfruit"),
    ("tallnut", "Tall-nut"),
    ("gatlingpea", "Gatling_Pea"),
    ("cobcannon", "Cob_Cannon"),
]

for p_key, p_wiki in plants:
    url = f"https://plantsvszombies.fandom.com/wiki/{p_wiki}/Gallery"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            # 查找所有图片 URL
            matches = re.findall(r'(https://static\.wikia\.nocookie\.net/plantsvszombies/images/[a-zA-Z0-9/_%-]+?\.(?:png|jpg|webp))', html)
            candidates = []
            for m in matches:
                # 过滤缩略图与修饰参数
                clean_url = m.split("/revision/")[0]
                lower = clean_url.lower()
                if "seed" in lower or "card" in lower or "packet" in lower:
                    candidates.append(clean_url)
            print(f"[{p_key}] Candidates: {len(candidates)}")
            if candidates:
                for c in set(candidates[:5]):
                    print("   ", c)
            else:
                # 打印含有植物名称的候选图
                name_candidates = [m.split('/revision/')[0] for m in matches if p_key[:5].lower() in m.lower()]
                for c in set(name_candidates[:3]):
                    print("   (alt)", c)
    except Exception as e:
        print(f"[{p_key}] Error: {e}")
