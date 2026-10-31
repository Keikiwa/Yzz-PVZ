@chcp 936 >nul
@echo off
setlocal
title PVZ - Gemini 4 Argon 复刻版本
cd /d "F:\Desktop\.DeskBox\文件夹\项目与开发\小游戏开发\10-pvz"

echo =======================================================
echo          PVZ - Gemini 4 Argon 复刻版本
echo =======================================================
echo [1] 真全屏支持：F11 / F / Alt+Enter / 右上角[全屏]按钮
echo [2] 自动吸附阳光：第 10 关解锁，右上角[自吸:开/关]随心切换
echo [3] 玉米投手优化：黄油必中追踪、30%%保底几率、伤害提升
echo [4] 双胞向日葵：阳光消耗修正为原版 125 阳光
echo [5] 读报僵尸与血条：常显稳定、报纸护甲纳入总血量
echo [6] 水上地图种植：6 行网格 100%% 像素级居中贴合
echo [7] 三线射手提前：白天草坪第 4 关解锁，第 5 关可用
echo =======================================================
echo 正在启动游戏，请稍候...

python pvz_ten_levels.py
if errorlevel 1 (
    echo [提示] 游戏已退出，退出代码：%errorlevel%
    pause
)
endlocal
