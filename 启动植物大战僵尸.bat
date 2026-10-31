@chcp 936 >nul
@echo off
setlocal
title PVZ - Gemini 4 Argon 复刻版本
cd /d "F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz"

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
