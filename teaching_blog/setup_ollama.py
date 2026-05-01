"""
Ollama 服务启动和模型管理工具
"""

import subprocess
import sys
import json
import requests
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

OLLAMA_BASE_URL = 'http://localhost:11434'


def check_ollama_installed():
    """检查Ollama是否已安装"""
    try:
        result = subprocess.run(
            ['ollama', '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print(f"[OK] Ollama 已安装")
            print(f"    版本: {result.stdout.strip()}")
            return True
        else:
            print("[FAIL] Ollama 未正确安装")
            return False
    except FileNotFoundError:
        print("[FAIL] Ollama 未安装或未添加到PATH")
        print("\n请先安装Ollama:")
        print("  访问: https://ollama.com/download")
        print("  下载并运行安装程序")
        return False
    except Exception as e:
        print(f"[ERROR] 检查失败: {e}")
        return False


def start_ollama_service():
    """启动Ollama服务"""
    print("\n[INFO] 正在启动 Ollama 服务...")

    try:
        # Windows系统
        if sys.platform == 'win32':
            # 后台启动Ollama服务
            subprocess.Popen(
                ['ollama', 'serve'],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("[OK] Ollama 服务已在后台启动")
            print("    请在新窗口中查看服务状态")

        elif sys.platform == 'darwin':  # macOS
            subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("[OK] Ollama 服务已启动")

        else:  # Linux
            subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("[OK] Ollama 服务已启动")

        import time
        time.sleep(3)  # 等待服务启动

        if check_service_running():
            return True
        else:
            print("[WARN] 服务可能未完全启动，请稍后手动检查")
            return True

    except Exception as e:
        print(f"[ERROR] 启动失败: {e}")
        print("\n手动启动方式:")
        print("  打开新终端，运行: ollama serve")
        return False


def check_service_running():
    """检查Ollama服务是否正在运行"""
    try:
        response = requests.get(f'{OLLAMA_BASE_URL}/api/tags', timeout=5)

        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            print(f"[OK] Ollama 服务运行正常")
            print(f"    地址: {OLLAMA_BASE_URL}")
            print(f"    已安装模型数: {len(models)}")

            if models:
                print("\n    已安装的模型:")
                for model in models:
                    size_gb = model.get('size', 0) / (1024**3)
                    modified = model.get('modified_at', '未知')
                    print(f"      • {model['name']} ({size_gb:.1f} GB)")

            return True
        else:
            print(f"[FAIL] 服务响应异常，状态码: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"[FAIL] 无法连接到 Ollama 服务 ({OLLAMA_BASE_URL})")
        print("    可能原因:")
        print("      1. Ollama 服务未启动")
        print("      2. 服务地址不正确")
        print("      3. 防火墙阻止连接")
        return False
    except Exception as e:
        print(f"[ERROR] 检查失败: {e}")
        return False


def download_model(model_name):
    """下载指定模型"""
    print(f"\n[INFO] 开始下载模型: {model_name}")
    print("=" * 50)

    try:
        process = subprocess.Popen(
            ['ollama', 'pull', model_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True
        )

        # 实时输出进度
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                line = output.strip()
                if line:
                    print(f"  {line}")

        return_code = process.wait()

        if return_code == 0:
            print(f"\n[OK] 模型 '{model_name}' 下载成功！✓")
            return True
        else:
            print(f"\n[FAIL] 模型下载失败，返回码: {return_code}")
            return False

    except KeyboardInterrupt:
        print("\n\n[WARN] 用户取消下载")
        process.terminate()
        return False
    except Exception as e:
        print(f"[ERROR] 下载过程出错: {e}")
        return False


def download_required_models():
    """下载RAG知识库所需的模型"""
    required_models = [
        {
            'name': 'qwen3:8b',
            'description': '大语言模型（用于AI问答）',
            'size': '~4.7 GB'
        },
        {
            'name': 'qwen3-embedding:4b',
            'description': '文本嵌入模型（用于文档向量化）',
            'size': '~2.3 GB'
        }
    ]

    print("\n" + "=" * 60)
    print("   RAG 知识库所需模型下载工具")
    print("=" * 60)

    print("\n需要下载以下模型:\n")

    for i, model in enumerate(required_models, 1):
        print(f"{i}. {model['name']}")
        print(f"   用途: {model['description']}")
        print(f"   大小: {model['size']}")
        print()

    total_size = "~7 GB"
    print(f"总计大小约: {total_size}")
    print(f"预计时间: 取决于网络速度（10Mbps约需10分钟）\n")

    confirm = input("是否开始下载？(y/n): ").lower()

    if confirm != 'y':
        print("[INFO] 用户取消")
        return

    success_count = 0

    for model_info in required_models:
        model_name = model_info['name']

        # 先检查是否已存在
        try:
            response = requests.get(f'{OLLAMA_BASE_URL}/api/show', json={'name': model_name}, timeout=5)
            if response.status_code == 200:
                print(f"\n[SKIP] 模型 '{model_name}' 已存在，跳过下载")
                success_count += 1
                continue
        except:
            pass

        # 下载模型
        if download_model(model_name):
            success_count += 1

        print()

    print("=" * 60)
    print(f"下载完成: {success_count}/{len(required_models)} 个模型")
    print("=" * 60)


def list_available_models():
    """列出所有可用模型"""
    print("\n[INFO] 获取可用的Ollama模型列表...\n")

    try:
        response = requests.get(f'{OLLAMA_BASE_URL}/api/tags', timeout=10)

        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])

            if not models:
                print("[INFO] 尚未安装任何模型")
                print("\n推荐下载:")
                print("  • qwen3:8b (LLM)")
                print("  • qwen3-embedding:4b (Embedding)")
            else:
                print(f"共找到 {len(models)} 个模型:\n")
                for i, model in enumerate(models, 1):
                    name = model.get('name', '未知')
                    size_bytes = model.get('size', 0)
                    size_mb = size_bytes / (1024 * 1024)
                    modified = model.get('modified_at', '未知')[:10]

                    print(f"{i}. {name}")
                    print(f"   大小: {size_mb:.1f} MB")
                    print(f"   更新: {modified}")
                    print()
        else:
            print(f"[FAIL] 获取失败，HTTP状态码: {response.status_code}")

    except requests.exceptions.ConnectionError:
        print("[FAIL] 无法连接到Ollama服务")
        print("请先启动Ollama服务: ollama serve")
    except Exception as e:
        print(f"[ERROR] {e}")


def test_model(model_name):
    """测试模型是否工作"""
    print(f"\n[INFO] 测试模型: {model_name}")
    print("-" * 40)

    try:
        payload = {
            'model': model_name,
            'prompt': '你好，请用一句话介绍自己。',
            'stream': False
        }

        response = requests.post(
            f'{OLLAMA_BASE_URL}/api/generate',
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            answer = result.get('response', '').strip()

            print("[OK] 模型响应成功 ✓")
            print(f"\n回答内容:\n{answer}\n")

            # 统计信息
            eval_count = result.get('eval_count', 0)
            eval_duration = result.get('eval_duration_ns', 0)
            total_duration = result.get('total_duration_ns', 0)

            if eval_duration > 0:
                eval_time_ms = eval_duration / 1_000_000
                tokens_per_sec = (eval_count / eval_time_ms) * 1000
                print(f"统计信息:")
                print(f"  • Token数量: {eval_count}")
                print(f"  • 生成耗时: {eval_time_ms:.1f} ms")
                print(f"  • 生成速度: {tokens_per_sec:.1f} tokens/s")

            return True
        else:
            print(f"[FAIL] API调用失败，状态码: {response.status_code}")
            return False

    except requests.exceptions.Timeout:
        print("[FAIL] 请求超时（30秒）")
        return False
    except Exception as e:
        print(f"[ERROR] 测试失败: {e}")
        return False


def main():
    """主菜单"""
    print("\n" + "=" * 60)
    print("       🤖 Ollama 服务管理工具")
    print("=" * 60)

    while True:
        print("\n请选择操作：")
        print("1. 检查 Ollama 是否已安装")
        print("2. 启动 Ollama 服务")
        print("3. 检查服务运行状态")
        print("4. 下载 RAG 所需模型 (qwen3:8b + embedding)")
        print("5. 列出已安装的模型")
        print("6. 测试 LLM 模型 (qwen3:8b)")
        print("7. 一键配置（安装+启动+下载）")
        print("8. 退出")

        choice = input("\n请输入选项 (1-8): ").strip()

        if choice == '1':
            check_ollama_installed()

        elif choice == '2':
            start_ollama_service()

        elif choice == '3':
            check_service_running()

        elif choice == '4':
            download_required_models()

        elif choice == '5':
            list_available_models()

        elif choice == '6':
            model = input("输入模型名称 (默认: qwen3:8b): ").strip() or 'qwen3:8b'
            test_model(model)

        elif choice == '7':
            print("\n开始一键配置...")
            if not check_ollama_installed():
                print("\n[STOP] 请先安装Ollama后再试")
                continue

            if not check_service_running():
                print("\n尝试启动服务...")
                start_ollama_service()
                import time
                time.sleep(5)

            if check_service_running():
                download_required_models()
            else:
                print("\n[FAIL] 服务启动失败，请手动启动后重试")

        elif choice == '8':
            print("\n再见！👋")
            break

        else:
            print("无效选项，请重新选择")

        input("\n按回车继续...")


if __name__ == '__main__':
    main()
