# -*- coding: utf-8 -*-
from pathlib import Path

doc_path = Path(r"F:\Desktop\.DeskBox\文件夹\反重力产出\文档\植物大战僵尸_Gemini4Argon复刻版本_V6更新与缺陷修复交付报告.md")
with open(doc_path, "r", encoding="utf-8-sig") as f:
    text = f.read()

cattail_section = """
### (9) 猫尾草制导刺针（Spike）自动残留彻底根除
- **智能全场重定向**：猫尾草发射的双重制导刺针在飞行途中，若锁定目标提前死亡，尖刺会自动且立即在全场存活僵尸中寻找新目标（优先追踪击落浮空气球僵尸，其次追踪最前排僵尸继续打击）；
- **动态倾角旋转渲染**：刺针在飞行追随过程中，贴图会根据飞行速度向量实时计算切线角度 `angle` 进行自然倾角旋转，针尖始终指向打击方向；
- **场面清空自然飞离**：当场上所有僵尸被全歼时，尖刺继续沿原轨迹疾飞滑出屏幕外自然销毁；
- **4.5 秒生命周期安全兜底**：单枚尖刺生存时间超过 4.5 秒强制消散自毁，命中后产生粉红晶莹爆破粒子，彻底消除任何尖刺残留与视觉卡顿。
"""

if "猫尾草制导刺针" not in text:
    insert_point = "## 3. 交付验证与文件清单"
    text = text.replace(insert_point, cattail_section + "\n---\n\n" + insert_point)

with open(doc_path, "wb") as f:
    f.write(b"\xef\xbb\xbf" + text.encode("utf-8"))

print("Updated delivery documentation with Cattail Spike fix (UTF-8 with BOM)!")
