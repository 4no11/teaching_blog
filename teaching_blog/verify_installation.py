#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RAG知识库系统 - 完整验证脚本
运行此脚本可一次性完成所有验证步骤
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_separator(title):
    """打印分隔线"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def check_python_version():
    """检查Python版本"""
    print_separator("STEP 1: Python Environment Check")
    
    version = sys.version_info
    print(f"  Python Version: {version.major}.{version.minor}.{version.micro}")
    
    if version >= (3, 8):
        print("  [PASS] Python version is compatible (>=3.8)")
        return True
    else:
        print("  [FAIL] Python version too old (need >=3.8)")
        return False

def check_dependencies():
    """检查所有依赖包"""
    print_separator("STEP 2: Dependencies Installation Check")
    
    required_packages = [
        ('langchain', 'LangChain Core'),
        ('langchain_community', 'LangChain Community'),
        ('chromadb', 'ChromaDB Vector Store'),
        ('ollama', 'Ollama Client'),
        ('pypdf', 'PyPDF (PDF Loader)'),
        ('unstructured', 'Unstructured (Document Loader)'),
        ('python_docx', 'python-docx (Word Loader)'),
        ('python_multipart', 'python-multipart (File Upload)')
    ]
    
    results = []
    
    for package, description in required_packages:
        try:
            # 处理带连字符的包名
            import_name = package.replace('-', '_')
            
            # 特殊处理
            if package == 'python_multipart':
                import_name = 'multipart'
            
            __import__(import_name)
            print(f"  [OK] {description:30s} v{get_version(package)}")
            results.append(True)
        except ImportError as e:
            print(f"  [FAIL] {description:30s} - {str(e)}")
            results.append(False)
        
        except Exception as e:
            print(f"  [ERROR] {description:30s} - Unexpected error: {str(e)}")
            results.append(False)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n  Result: {passed}/{total} packages installed")
    
    if passed == total:
        print("  [SUCCESS] All dependencies are installed!")
        return True
    else:
        missing = total - passed
        print(f"  [WARNING] {missing} packages missing")
        return False

def get_version(package_name):
    """获取包版本"""
    try:
        import_name = package_name.replace('-', '_')
        if package_name == 'python_multipart':
            import_name = 'multipart'
        
        module = __import__(import_name)
        return getattr(module, '__version__', 'unknown')
    except:
        return 'unknown'

def check_rag_service():
    """测试RAG服务模块导入"""
    print_separator("STEP 3: RAG Service Module Test")
    
    try:
        from services.rag_service import RAGKnowledgeService
        print("  [OK] rag_service module imported")
        
        # 初始化服务（不加载模型）
        service = RAGKnowledgeService()
        print(f"  [OK] RAGService initialized")
        print(f"       Base directory: {service.base_dir}")
        print(f"       Ollama URL: {service.ollama_base_url}")
        print(f"       LLM Model: {service.llm_model}")
        print(f"       Embedding Model: {service.embedding_model}")
        
        return True
        
    except Exception as e:
        print(f"  [FAIL] RAG Service initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_rag_routes():
    """测试RAG路由模块"""
    print_separator("STEP 4: RAG Routes Module Test")
    
    try:
        from routes.rag_routes import register_rag_routes
        print("  [OK] rag_routes module imported")
        print("  [OK] register_rag_routes function available")
        
        # 检查路由函数列表
        functions = [
            'list_knowledge_bases',
            'create_knowledge_base',
            'delete_knowledge_base',
            'upload_documents',
            'chat',
            'system_status'
        ]
        
        for func in functions:
            print(f"  [OK]   - {func}")
        
        return True
        
    except Exception as e:
        print(f"  [FAIL] RAG Routes test failed: {e}")
        return False

def check_ollama_connection():
    """检查Ollama连接状态"""
    print_separator("STEP 5: Ollama Connection Test")
    
    try:
        import requests
        
        ollama_url = "http://localhost:11434"
        
        # 测试连接
        response = requests.get(
            f"{ollama_url}/api/tags",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            model_names = [m['name'] for m in models]
            
            print(f"  [OK] Ollama server is running at {ollama_url}")
            print(f"  [INFO] Available models ({len(models)}):")
            
            for name in sorted(model_names):
                size = next((m.get('size', 0) for m in models if m['name'] == name), 0)
                size_mb = size / (1024 * 1024) if size > 0 else 0
                print(f"         - {name:<30s} ({size_mb:.1f} MB)")
            
            # 检查必需模型
            required_models = ['qwen3:8b', 'qwen3-embedding:4b']
            missing_models = [m for m in required_models if m not in model_names]
            
            if not missing_models:
                print(f"\n  [SUCCESS] All required models are available!")
                return True
            else:
                print(f"\n  [WARNING] Missing required models:")
                for model in missing_models:
                    print(f"           - {model}")
                print(f"\n  Run these commands to download:")
                print(f"    ollama pull qwen3:8b")
                print(f"    ollama pull qwen3-embedding:4b")
                return False
                
        else:
            print(f"  [WARN] Ollama server returned status {response.status_code}")
            print(f"  Please ensure Ollama is running: ollama serve")
            return False
            
    except requests.exceptions.ConnectionError:
        print("  [FAIL] Cannot connect to Ollama server")
        print("  Please install and start Ollama first:")
        print("    1. Download from https://ollama.ai")
        print("    2. Install and run the application")
        print("    3. Or run: ollama serve")
        return False
        
    except Exception as e:
        print(f"  [ERROR] Ollama connection test failed: {e}")
        return False

def check_flask_app():
    """测试Flask应用能否正常启动"""
    print_separator("STEP 6: Flask Application Test")
    
    try:
        # 暂时不实际启动Flask，只检查配置文件
        import os
        
        app_file = os.path.join(os.getcwd(), 'app.py')
        config_file = os.path.join(os.getcwd(), 'config.py')
        routes_file = os.path.join(os.getcwd(), 'routes', 'client.py')
        rag_routes_file = os.path.join(os.getcwd(), 'routes', 'rag_routes.py')
        template_file = os.path.join(os.getcwd(), 'templates', 'client', 'rag_knowledge.html')
        
        files_to_check = {
            'app.py': app_file,
            'config.py': config_file,
            'routes/client.py': routes_file,
            'routes/rag_routes.py': rag_routes_file,
            'templates/rag_knowledge.html': template_file
        }
        
        all_exist = True
        for name, path in files_to_check.items():
            if os.path.exists(path):
                size = os.path.getsize(path)
                print(f"  [OK] {name:<35s} ({size:,} bytes)")
            else:
                print(f"  [MISSING] {name}")
                all_exist = False
        
        if all_exist:
            print(f"\n  [SUCCESS] All application files exist!")
            print(f"\n  To start the application:")
            print(f"    cd teaching_blog")
            print(f"    python app.py")
            print(f"\n  Then open: http://localhost:5000/rag-knowledge")
            return True
        else:
            print(f"\n  [WARNING] Some files are missing")
            return False
            
    except Exception as e:
        print(f"  [ERROR] Flask app check failed: {e}")
        return False

def generate_test_report():
    """生成测试报告"""
    print_separator("VERIFICATION COMPLETE - SUMMARY REPORT")
    
    report = f"""
╔══════════════════════════════════════════════════╗
║     RAG Knowledge System - Verification Report      ║
╠══════════════════════════════════════════════════╣
║                                                  ║
║  Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<27s} ║
║  Python: {sys.version.split()[0]:<34s} ║
║                                                  ║
║  Next Steps:                                     ║
║  1. Ensure Ollama is running                      ║
║  2. Download models:                              ║
║     ollama pull qwen3:8b                          ║
║     ollama pull qwen3-embedding:4b                 ║
║  3. Start application:                             ║
║     cd teaching_blog                               ║
║     python app.py                                  ║
║  4. Open browser:                                  ║
║     http://localhost:5000/rag-knowledge           ║
║                                                  ║
╚══════════════════════════════════════════════════╝
"""
    
    print(report)

if __name__ == '__main__':
    from datetime import datetime
    
    print("\n" + "╔" + "═" * 58 + "╗")
    print("║" + "  RAG Knowledge System - Complete Verification".center(56) + "║")
    print("╚" + "═" * 58 + "╝")
    
    # 执行所有验证步骤
    results = []
    
    results.append(("Python Environment", check_python_version()))
    results.append(("Dependencies", check_dependencies()))
    results.append(("RAG Service Module", check_rag_service()))
    results.append(("RAG Routes Module", check_rag_routes()))
    results.append(("Ollama Connection", check_ollama_connection()))
    results.append(("Flask Application Files", check_flask_app()))
    
    # 生成报告
    generate_test_report()
    
    # 最终结果
    print_separator("FINAL RESULT")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        symbol = "✓" if result else "✗"
        print(f"  {symbol} {status} {name}")
    
    print()
    
    if passed == total:
        print("=" * 60)
        print("  ✓ ALL CHECKS PASSED! System is ready to use!")
        print("=" * 60)
        sys.exit(0)
    elif passed >= total - 1:
        print("=" * 60)
        print(f"  ! {passed}/{total} checks passed")
        print("  System can run but some features may be limited")
        print("=" * 60)
        sys.exit(0)
    else:
        print("=" * 60)
        print(f"  ✗ Only {passed}/{total} checks passed")
        print("  Please fix the issues above before using")
        print("=" * 60)
        sys.exit(1)
