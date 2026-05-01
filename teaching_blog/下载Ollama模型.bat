@echo off
chcp 65001 > nul
title Ollama 轻量模型下载器
color 0B

echo.
echo ╔════════════════════════════════════════════════╗
echo ║    📦 Ollama 轻量级模型 快速下载工具          ║
echo ╚════════════════════════════════════════════════╝
echo.

REM 检查Ollama
where ollama >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 请先安装Ollama: https://ollama.com/download
    pause
    exit /b 1
)

echo 当前已安装的模型:
echo ────────────────────────────────
ollama list 2>nul || echo (无)
echo ────────────────────────────────
echo.

echo 请选择要下载的模型版本:
echo.
echo   [1] 🟢 超轻量版 (推荐！8GB内存电脑)
echo       ├─ qwen3:4b         (~1.8GB) - LLM大语言模型
echo       └─ nomic-embed-text (~274MB) - 文本向量化
echo       总计: ~2.1GB | 内存占用: ~3GB | 速度快⚡
echo.
echo   [2] 🔵 标准版 (16GB+内存电脑)
echo       ├─ qwen3:8b           (~4.7GB) - LLM大语言模型
echo       └─ qwen3-embedding:4b (~2.3GB) - 文本向量化
echo       总计: ~7.0GB | 内存占用: ~6-8GB | 效果更好
echo.
echo   [3] 仅下载 LLM 模型
echo   [4] 仅下载 Embedding 模型
echo   [5] 显示所有可用模型
echo   [0] 退出
echo.

set /p choice="请输入选项 (0-5): "

if "%choice%"=="1" goto light
if "%choice%"=="2" goto standard
if "%choice%"=="3" goto llm_only
if "%choice%"=="4" goto embed_only
if "%choice%"=="5" goto show_all
if "%choice%"=="0" goto end

echo ❌ 无效选项
pause
goto end

:light
echo.
echo ══════════════════════════════════════
echo   📥 开始下载超轻量版模型...
echo ══════════════════════════════════════
echo.

echo [1/2] 下载 LLM: qwen3:4b
echo ─────────────────────────────────
ollama pull qwen3:4b
if %errorlevel% neq 0 (
    echo.
    echo ❌ 下载失败！请检查网络连接
    pause
    goto end
)
echo ✅ 完成
echo.

echo [2/2] 下载 Embedding: nomic-embed-text
echo ────────────────────────────────────────
ollama pull nomic-embed-text
if %errorlevel% neq 0 (
    echo.
    echo ❌ 下载失败！请检查网络连接
    pause
    goto end
)
echo ✅ 完成
echo.

echo ══════════════════════════════════════
echo   ✅ 超轻量版模型全部安装完成！
echo ══════════════════════════════════════
echo.
echo 已安装的模型:
ollama list
echo.
echo 下一步: 双击 "启动RAG知识库.bat" 启动系统
echo.
pause
goto end

:standard
echo.
echo ══════════════════════════════════════
echo   📥 开始下载标准版模型...
echo ══════════════════════════════════════
echo.

echo [1/2] 下载 LLM: qwen3:8b
echo ─────────────────────────────────
ollama pull qwen3:8b
if %errorlevel% neq 0 (
    echo.
    echo ❌ 下载失败！请检查网络连接
    pause
    goto end
)
echo ✅ 完成
echo.

echo [2/2] 下载 Embedding: qwen3-embedding:4b
echo ─────────────────────────────────────────
ollama pull qwen3-embedding:4b
if %errorlevel% neq 0 (
    echo.
    echo ❌ 下载失败！请检查网络连接
    pause
    goto end
)
echo ✅ 完成
echo.

echo ══════════════════════════════════════
echo   ✅ 标准版模型全部安装完成！
echo ══════════════════════════════════════
echo.
echo ⚠️  注意：标准版需要修改配置文件才能使用：
echo      编辑 services\rag_service.py 第64-65行，改为：
echo        self.llm_model = 'qwen3:8b'
echo        self.embedding_model = 'qwen3-embedding:4b'
echo.
pause
goto end

:llm_only
echo.
echo 下载 LLM: qwen3:4b ...
ollama pull qwen3:4b
if %errorlevel% equ 0 (
    echo ✅ 下载完成
) else (
    echo ❌ 下载失败
)
pause
goto end

:embed_only
echo.
echo 下载 Embedding: nomic-embed-text ...
ollama pull nomic-embed-text
if %errorlevel% equ 0 (
    echo ✅ 下载完成
) else (
    echo ❌ 下载失败
)
pause
goto end

:show_all
echo.
echo 可用的轻量级中文模型推荐:
echo ────────────────────────────────────────
echo.
echo LLM 大语言模型:
echo   • qwen3:1.7b     (~1.0GB) - 最小，速度最快
echo   • qwen3:4b       (~1.8GB) - 推荐✓ 平衡
echo   • qwen3:8b       (~4.7GB) - 效果好
echo.
echo Embedding 向量化模型:
echo   • nomic-embed-text  (~274MB) - 推荐✓ 轻量
echo   • mxbai-embed-large (~670MB) - 效果好
echo   • qwen3-embedding:4b (~2.3GB) - 中文优化
echo.
pause
goto end

:end
