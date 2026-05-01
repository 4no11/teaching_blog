@echo off
chcp 65001 > nul
title RAG 知识库系统 - 轻量版
color 0A

echo.
echo ╔════════════════════════════════════════════════╗
echo ║       🤖 RAG 知识库系统 - 一键启动器           ║
echo ║       (Ollama 轻量版 | 8GB内存优化)            ║
echo ╚════════════════════════════════════════════════╝
echo.

REM ==================== 第1步：检查Ollama ====================
echo [1/4] 检查 Ollama 安装状态...

where ollama >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ❌ 未检测到 Ollama！
    echo.
    echo 请先安装 Ollama：
    echo   1. 访问 https://ollama.com/download
    echo   2. 下载 Windows 版本
    echo   3. 运行安装程序
    echo   4. 完成后重新运行此脚本
    echo.
    pause
    exit /b 1
)

echo ✅ Ollama 已安装
echo.

REM ==================== 第2步：启动Ollama服务 ====================
echo [2/4] 启动 Ollama 服务...

REM 检查Ollama是否已在运行
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Ollama 服务已在运行
) else (
    echo 正在启动 Ollama 服务（新窗口）...
    start "Ollama Service" /min ollama serve

    REM 等待服务启动
    echo 等待服务启动...
    timeout /t 5 /nobreak > nul

    REM 再次检查
    curl -s http://localhost:11434/api/tags >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Ollama 服务启动成功
    ) else (
        echo ⚠️  Ollama 服务可能未完全启动，继续尝试...
        timeout /t 3 /nobreak > nul
    )
)
echo.

REM ==================== 第3步：检查并下载模型 ====================
echo [3/4] 检查所需模型...

REM 检查LLM模型
ollama list 2>nul | findstr "qwen3:4b" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ LLM模型已安装: qwen3:4b
) else (
    echo.
    echo 📥 正在下载轻量级LLM模型: qwen3:4b (~1.8GB)
    echo    首次下载可能需要几分钟，请耐心等待...
    echo.
    ollama pull qwen3:4b
    if %errorlevel% equ 0 (
        echo ✅ LLM模型下载完成
    ) else (
        echo ❌ LLM模型下载失败！请检查网络连接
        pause
        exit /b 1
    )
)

REM 检查Embedding模型
ollama list 2>nul | findstr "nomic-embed-text" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Embedding模型已安装: nomic-embed-text
) else (
    echo.
    echo 📥 正在下载轻量级Embedding模型: nomic-embed-text (~274MB)
    echo.
    ollama pull nomic-embed-text
    if %errorlevel% equ 0 (
        echo ✅ Embedding模型下载完成
    ) else (
        echo ❌ Embedding模型下载失败！请检查网络连接
        pause
        exit /b 1
    )
)
echo.

REM 显示已安装的模型
echo 已安装的模型列表:
ollama list
echo.

REM ==================== 第4步：启动Flask应用 ====================
echo [4/4] 启动 RAG 知识库系统...
echo.
echo ════════════════════════════════════════
echo   🎉 系统启动中...
echo   访问地址: http://localhost:5000/rag
echo   按 Ctrl+C 停止服务
echo ════════════════════════════════════════
echo.

REM 切换到项目目录
cd /d "%~dp0"

REM 启动Flask应用
python app.py

echo.
echo 系统已停止
pause
