@echo off
chcp 65001 >nul

REM 师备云启动脚本

echo ========================================
echo     师备云 - 启动中...
echo ========================================
echo.
echo AI配置: 硅基流动 (已内置)
echo.

echo 正在启动Flask应用...
set FLASK_APP=app.py

python -m flask run --host=0.0.0.0 --port=5000

pause
