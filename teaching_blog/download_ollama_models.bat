@echo off
chcp 65001 > nul
echo ============================================
echo    Ollama 轻量级模型 一键配置工具
echo ============================================
echo.

echo [检查] 正在检查 Ollama 是否已安装...
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [错误] Ollama 未安装！
    echo.
    echo 请先安装 Ollama：
    echo   访问 https://ollama.com/download
    echo   下载并运行安装程序
    echo.
    pause
    exit /b 1
)

echo [OK] Ollama 已安装
echo.

echo ============================================
echo    请选择要下载的模型版本：
echo ============================================
echo.
echo   [1] 超轻量版 (推荐 8GB内存电脑)
echo       模型: qwen3:4b + nomic-embed-text
echo       总大小: ~2.1 GB
echo       内存占用: ~3 GB
echo       速度: 快 ⚡
echo.
echo   [2] 标准版 (推荐 16GB内存电脑)
echo       模型: qwen3:8b + qwen3-embedding:4b
echo       总大小: ~7.0 GB
echo       内存占用: ~6-8 GB
echo       速度: 中等
echo.
echo   [3] 仅下载 LLM (已有Embedding)
echo.
echo   [4] 仅下载 Embedding (已有LLM)
echo.
echo   [0] 退出
echo.

set /p choice="请输入选项 (0-4): "

if "%choice%"=="1" goto light
if "%choice%"=="2" goto standard
if "%choice%"=="3" goto llm_only
if "%choice%"=="4" goto embed_only
if "%choice%"=="0" goto end

echo 无效选项
pause
goto end

:light
echo.
echo ============================================
echo    开始下载超轻量版模型...
echo ============================================
echo.
echo [1/2] 下载 LLM: qwen3:4b (~1.8GB)...
call ollama pull qwen3:4b
if %errorlevel% neq 0 (
    echo [错误] LLM下载失败！
    pause
    goto end
)
echo [OK] LLM下载完成
echo.
echo [2/2] 下载 Embedding: nomic-embed-text (~274MB)...
call ollama pull nomic-embed-text
if %errorlevel% neq 0 (
    echo [错误] Embedding下载失败！
    pause
    goto end
)
echo [OK] Embedding下载完成
echo.
echo ============================================
echo    ✅ 超轻量版模型下载完成！
echo ============================================
echo.
echo 已安装模型:
call ollama list
echo.
echo 下一步:
echo   1. 运行 setup_lightweight.bat 配置项目
echo   2. 启动 RAG 知识库系统
echo.
pause
goto end

:standard
echo.
echo ============================================
echo    开始下载标准版模型...
echo ============================================
echo.
echo [1/2] 下载 LLM: qwen3:8b (~4.7GB)...
call ollama pull qwen3:8b
if %errorlevel% neq 0 (
    echo [错误] LLM下载失败！
    pause
    goto end
)
echo [OK] LLM下载完成
echo.
echo [2/2] 下载 Embedding: qwen3-embedding:4b (~2.3GB)...
call ollama pull qwen3-embedding:4b
if %errorlevel% neq 0 (
    echo [错误] Embedding下载失败！
    pause
    goto end
)
echo [OK] Embedding下载完成
echo.
echo ============================================
echo    ✅ 标准版模型下载完成！
echo ============================================
echo.
echo 已安装模型:
call ollama list
echo.
pause
goto end

:llm_only
echo.
echo [INFO] 下载 LLM: qwen3:4b ...
call ollama pull qwen3:4b
if %errorlevel% equ 0 (
    echo [OK] 下载完成
) else (
    echo [错误] 下载失败
)
pause
goto end

:embed_only
echo.
echo [INFO] 下载 Embedding: nomic-embed-text ...
call ollama pull nomic-embed-text
if %errorlevel% equ 0 (
    echo [OK] 下载完成
) else (
    echo [错误] 下载失败
)
pause
goto end

:end
