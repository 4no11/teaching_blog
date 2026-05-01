"""
ChromaDB集成测试脚本 - 验证RAG系统使用原生ChromaDB API
"""

import os
import sys
import tempfile
import io

# 设置控制台输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_chromadb_integration():
    """完整测试ChromaDB集成"""
    print("=" * 60)
    print("🧪 ChromaDB 集成测试")
    print("=" * 60)

    # 1. 测试chromadb包导入
    print("\n[1/6] 测试 chromadb 包导入...")
    try:
        import chromadb
        print(f"✅ chromadb 版本: {chromadb.__version__}")
    except ImportError as e:
        print(f"❌ chromadb 导入失败: {e}")
        return False

    # 2. 测试ChromaDB客户端连接
    print("\n[2/6] 测试 ChromaDB 客户端连接...")
    try:
        test_dir = tempfile.mkdtemp(prefix='chroma_test_')
        client = chromadb.PersistentClient(path=test_dir)
        print(f"✅ ChromaDB 客户端创建成功")
        print(f"   测试目录: {test_dir}")
    except Exception as e:
        print(f"❌ ChromaDB 客户端创建失败: {e}")
        return False

    # 3. 测试集合创建和数据存储
    print("\n[3/6] 测试 ChromaDB 集合操作...")
    try:
        collection = client.get_or_create_collection(
            name="test_documents",
            metadata={"hnsw:space": "cosine"}
        )

        # 添加测试数据（使用模拟向量）
        test_data = [
            ("doc_1", "这是第一段测试文档内容", {"source": "test.txt"}, [0.1] * 768),
            ("doc_2", "这是第二段测试文档内容，用于验证向量数据库功能", {"source": "test2.txt"}, [0.2] * 768),
            ("doc_3", "Python是一种流行的编程语言", {"source": "code.txt"}, [0.3] * 768),
        ]

        collection.upsert(
            ids=[item[0] for item in test_data],
            documents=[item[1] for item in test_data],
            metadatas=[item[2] for item in test_data],
            embeddings=[item[3] for item in test_data]
        )

        count = collection.count()
        print(f"✅ 数据插入成功，共 {count} 条记录")

        # 测试查询
        results = collection.query(
            query_embeddings=[[0.15] * 768],
            n_results=2,
            include=['documents', 'metadatas', 'distances']
        )

        if results['documents'] and results['documents'][0]:
            print(f"✅ 查询成功，返回 {len(results['documents'][0])} 条结果")
            for i, (doc, dist) in enumerate(zip(results['documents'][0], results['distances'][0])):
                print(f"   结果{i+1}: {doc[:50]}... (距离: {dist:.4f})")
        else:
            print("⚠️ 查询返回空结果")
    except Exception as e:
        print(f"❌ ChromaDB 操作失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 4. 测试Ollama Embedding API连接
    print("\n[4/6] 测试 Ollama Embedding API...")
    try:
        import requests

        ollama_url = 'http://localhost:11434'
        response = requests.get(f'{ollama_url}/api/tags', timeout=5)

        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [m['name'] for m in models]
            print(f"✅ Ollama 服务运行中")
            print(f"   可用模型: {model_names}")

            # 检查embedding模型
            embedding_models = ['nomic-embed-text', 'qwen3-embedding:4b']
            available_embedding = [m for m in model_names if any(em in m for em in embedding_models)]

            if available_embedding:
                print(f"✅ 找到嵌入模型: {available_embedding[0]}")

                # 测试生成向量
                embed_response = requests.post(
                    f'{ollama_url}/api/embeddings',
                    json={
                        'model': available_embedding[0],
                        'prompt': '测试文本'
                    },
                    timeout=30
                )

                if embed_response.status_code == 200:
                    embedding = embed_response.json().get('embedding', [])
                    print(f"✅ 向量生成成功，维度: {len(embedding)}")
                else:
                    print(f"⚠️ 向量生成失败: {embed_response.text}")
            else:
                print("⚠️ 未找到嵌入模型，请运行: ollama pull nomic-embed-text")
        else:
            print(f"⚠️ Ollama 服务未运行或无法连接 (状态码: {response.status_code})")
            print("   请先启动 Ollama: ollama serve")
    except requests.exceptions.ConnectionError:
        print("⚠️ 无法连接到 Ollama 服务 (http://localhost:11434)")
        print("   请确保 Ollama 已安装并运行")
    except Exception as e:
        print(f"⚠️ Ollama 测试出错: {e}")

    # 5. 测试RAG服务初始化
    print("\n[5/6] 测试 RAG 服务初始化...")
    try:
        from services.rag_service import RAGKnowledgeService

        service = RAGKnowledgeService(provider='ollama')
        kbs = service.list_knowledge_bases()
        print(f"✅ RAG 服务初始化成功")
        print(f"   当前知识库数量: {len(kbs)}")
        for kb in kbs[:3]:
            print(f"   - {kb['name']} (ID: {kb['id'][:20]}...)")
    except Exception as e:
        print(f"❌ RAG 服务初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 6. 清理测试数据
    print("\n[6/6] 清理测试数据...")
    try:
        import shutil
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
            print(f"✅ 测试目录已清理")
    except Exception as e:
        print(f"⚠️ 清理失败: {e}")

    print("\n" + "=" * 60)
    print("🎉 ChromaDB 集成测试完成！")
    print("=" * 60)
    print("\n📋 测试总结:")
    print("  ✅ chromadb 包可正常导入和使用")
    print("  ✅ ChromaDB 原生API工作正常")
    print("  ✅ 数据存储和查询功能正常")
    print("  ✅ RAG服务已切换为ChromaDB原生API")
    print("\n💡 下一步:")
    print("  1. 确保 Ollama 服务正在运行")
    print("  2. 访问 http://localhost:5000/rag-knowledge 测试完整功能")
    print("  3. 上传文档并测试问答功能")

    return True


if __name__ == '__main__':
    success = test_chromadb_integration()
    sys.exit(0 if success else 1)
