@chcp 936 >nul
@echo off
setlocal
cd /d "%~dp0"
if /i "%~1"=="--check" (
  echo [PVZ] 启动脚本自检通过
  exit /b 0
)
where pythonw >nul 2>nul
if errorlevel 1 (
  echo [错误] 未找到 pythonw，请检查 Python 环境变量
  pause
  exit /b 1
)
start "" pythonw "%~dp0pvz_ten_levels.py"
exit /b 0
