# -*- coding: utf-8 -*-
"""更新交付脚本与交付文档文案，彻底去除浮夸称呼，统一标注为：
PVZ - Gemini 4 Argon 复刻版本
严格遵守 GBK+CRLF 及 UTF-8 with BOM 规范。
"""
import os

OUTPUT_BASE = r"F:\Desktop\.DeskBox\文件夹\反重力产出"
SCRIPT_PATH = os.path.join(OUTPUT_BASE, "脚本", "启动植物大战僵尸.bat")
DOC_DIR = os.path.join(OUTPUT_BASE, "文档")
GAME_DIR = r"F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz"

# 1. 启动脚本 (GBK + CRLF)
bat_content = """@chcp 936 >nul
@echo off
setlocal
title PVZ - Gemini 4 Argon 复刻版本
cd /d "F:\\Desktop\\.DeskBox\\文件夹\\项目与开发\\小游戏开发\\10-pvz"

echo =======================================================
echo          PVZ - Gemini 4 Argon 复刻版本
echo =======================================================
echo [1] 34 种植物机制与动画序列帧已装配
echo [2] 卡牌阳光数值与原版徽章正常显示
echo [3] 泳池关卡（第 11 关）双水路植物对齐
echo [4] 支持按键快捷跳关与自选关卡体验
echo =======================================================
echo 正在启动游戏，请稍候...

python pvz_ten_levels.py
if errorlevel 1 (
    echo [提示] 游戏已退出，退出代码：%errorlevel%
    pause
)
endlocal
"""

with open(SCRIPT_PATH, "wb") as f:
    f.write(bat_content.replace("\r\n", "\n").replace("\n", "\r\n").encode("gbk"))
with open(os.path.join(GAME_DIR, "启动植物大战僵尸.bat"), "wb") as f:
    f.write(bat_content.replace("\r\n", "\n").replace("\n", "\r\n").encode("gbk"))
print("Updated .bat scripts in GBK + CRLF.")

# 2. 交付文档 (UTF-8 with BOM)
# 清理旧名称文档
old_doc = os.path.join(DOC_DIR, "植物大战僵尸_全功能豪华版_交付说明.md")
if os.path.exists(old_doc):
    os.remove(old_doc)
    print("Removed old luxury-titled doc.")

new_doc_path = os.path.join(DOC_DIR, "植物大战僵尸_Gemini4Argon复刻版本_交付说明.md")

doc_content = """# 植物大战僵尸 (PVZ) - Gemini 4 Argon 复刻版本说明

> **项目名称**：PVZ - Gemini 4 Argon 复刻版本  
> **开源仓库**：[GitHub - SherlockYzz/PVZ-Gemini-4-Argon](https://github.com/SherlockYzz/PVZ-Gemini-4-Argon)  
> **本地启动**：[`启动植物大战僵尸.bat`](file:///F:/Desktop/.DeskBox/文件夹/反重力产出/脚本/启动植物大战僵尸.bat)  
> **实机截图**：[`植物大战僵尸_大喷菇与全卡牌修复实机展示.png`](file:///F:/Desktop/.DeskBox/文件夹/反重力产出/图片/植物大战僵尸_大喷菇与全卡牌修复实机展示.png)  

---

## 一、 项目背景与真实定位

本项目是一个基于 **Python + Pygame** 构建的《植物大战僵尸》基础机制复刻与学习项目，由开发者与 **Gemini 4 Argon** 协同完成。  
我们遵循求真、务实、谦逊的开发态度，旨在探索 2D 塔防游戏的核心循环、网格判定、动画状态机流转与关卡调度逻辑。

---

## 二、 核心实现与近期修复

1. **大喷菇细节还原**：
   - 补全原版卡片阳光费用“75”及金色阳光徽章，彻底解决此前卡槽底框空白的问题；
   - 接入 18 帧官方原版动画（待机呼吸 + 喷射攻击），替换掉早期的单色简笔画假图。
2. **全 34 种植物卡牌与立绘复核**：
   - 全面排查所有 34 种植物，解决高坚果（125）、魅惑菇（75）、毁灭菇（125）、杨桃（125）底框空白问题，卡牌数值 100% 正常；
   - 高坚果实装 51 帧正版原貌（含完整战损裂痕）；机枪射手实装 19 帧迷彩钢盔四管机枪正版动作；激光豆、魔术菇、龙舌兰等均已适配。
3. **水路泳池关卡（第 11 关）**：
   - 针对泳池专属网格进行了居中校准，睡莲与水上植物（猫尾草、高坚果等）精准种入蓝色水面区域，不再种到水泥边堤。
4. **调试与跳关支持**：
   - 右上角设有传送门与快捷关卡切换按钮，支持在 1~11 关之间自由跳转体验。

---

## 三、 GitHub 开源托管信息

- **Repository**：`SherlockYzz/PVZ-Gemini-4-Argon`
- **URL**：https://github.com/SherlockYzz/PVZ-Gemini-4-Argon
- **Git Remote**：`git@github.com:SherlockYzz/PVZ-Gemini-4-Argon.git`
- **遵循协议**：仅供技术学习与交流，素材版权归原版公司所有。

---

## 四、 交付产物清单

- **启动脚本**：
  - [启动植物大战僵尸.bat](file:///F:/Desktop/.DeskBox/文件夹/反重力产出/脚本/启动植物大战僵尸.bat)（GBK + CRLF 编码）
- **交付文档**：
  - [植物大战僵尸_Gemini4Argon复刻版本_交付说明.md](file:///F:/Desktop/.DeskBox/文件夹/反重力产出/文档/植物大战僵尸_Gemini4Argon复刻版本_交付说明.md)（UTF-8 with BOM 编码）
- **效果截图**：
  - [植物大战僵尸_大喷菇与全卡牌修复实机展示.png](file:///F:/Desktop/.DeskBox/文件夹/反重力产出/图片/植物大战僵尸_大喷菇与全卡牌修复实机展示.png)
  - [植物大战僵尸_顶部卡槽阳光数值清晰展示.png](file:///F:/Desktop/.DeskBox/文件夹/反重力产出/图片/植物大战僵尸_顶部卡槽阳光数值清晰展示.png)
  - [植物大战僵尸_大喷菇与新立绘特写.png](file:///F:/Desktop/.DeskBox/文件夹/反重力产出/图片/植物大战僵尸_大喷菇与新立绘特写.png)
"""

with open(new_doc_path, "wb") as f:
    f.write(doc_content.encode("utf-8-sig"))
print(f"Updated {new_doc_path} in UTF-8 with BOM.")
