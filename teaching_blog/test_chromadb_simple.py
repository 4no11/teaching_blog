# -*- coding: utf-8 -*-
"""
ChromaDB基本功能测试
"""

import os
import sys
import tempfile
import shutil

def test_basic_chromadb():
    """测试ChromaDB基本功能"""
    print("Testing ChromaDB...")

    # 1. 导入测试
    try:
        import chromadb
        print(f"[OK] chromadb imported, version: {chromadb.__version__}")
    except Exception as e:
        print(f"[FAIL] Cannot import chromadb: {e}")
        return False

    # 2. 创建客户端
    try:
        test_dir = tempfile.mkdtemp(prefix='chroma_test_')
        client = chromadb.PersistentClient(path=test_dir)
        print(f"[OK] Client created at: {test_dir}")
    except Exception as e:
        print(f"[FAIL] Client creation failed: {e}")
        return False

    # 3. 创建集合
    try:
        collection = client.get_or_create_collection(
            name="test_collection",
            metadata={"hnsw:space": "cosine"}
        )
        print("[OK] Collection created")
    except Exception as e:
        print(f"[FAIL] Collection creation failed: {e}")
        return False

    # 4. 插入数据
    try:
        collection.upsert(
            ids=["doc1", "doc2", "doc3"],
            documents=["Hello world", "Test document", "Python programming"],
            metadatas=[{"source": "a"}, {"source": "b"}, {"source": "c"}],
            embeddings=[[0.1]*768, [0.2]*768, [0.3]*768]
        )
        count = collection.count()
        print(f"[OK] Inserted {count} documents")
    except Exception as e:
        print(f"[FAIL] Data insertion failed: {e}")
        return False

    # 5. 查询数据
    try:
        results = collection.query(
            query_embeddings=[[0.15]*768],
            n_results=2,
            include=['documents', 'metadatas', 'distances']
        )

        if results['documents'] and results['documents'][0]:
            print(f"[OK] Query returned {len(results['documents'][0])} results")
            for i, doc in enumerate(results['documents'][0]):
                print(f"  - Result {i+1}: {doc[:40]}...")
        else:
            print("[WARN] Query returned empty")
    except Exception as e:
        print(f"[FAIL] Query failed: {e}")
        return False

    # 6. 清理
    try:
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        print("[OK] Cleanup completed")
    except Exception as e:
        print(f"[WARN] Cleanup failed: {e}")

    print("\n" + "="*50)
    print("SUCCESS: All ChromaDB tests passed!")
    print("="*50)
    return True


def test_ollama_connection():
    """测试Ollama连接"""
    import requests

    print("\nTesting Ollama connection...")

    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)

        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            model_names = [m['name'] for m in models]
            print(f"[OK] Ollama is running")
            print(f"     Available models: {model_names}")

            # Check for embedding models
            embed_models = [m for m in model_names if 'embed' in m.lower()]
            if embed_models:
                print(f"[OK] Found embedding model: {embed_models[0]}")

                # Test embedding generation
                resp = requests.post(
                    'http://localhost:11434/api/embeddings',
                    json={'model': embed_models[0], 'prompt': 'test'},
                    timeout=30
                )

                if resp.status_code == 200:
                    emb = resp.json().get('embedding', [])
                    print(f"[OK] Embedding generated, dim={len(emb)}")
                    return True
                else:
                    print(f"[WARN] Embedding failed: {resp.text}")
            else:
                print("[WARN] No embedding model found")
                print("       Run: ollama pull nomic-embed-text")
        else:
            print(f"[WARN] Ollama returned status {response.status_code}")

    except requests.exceptions.ConnectionError:
        print("[WARN] Ollama not running at http://localhost:11434")
        print("       Start with: ollama serve")
    except Exception as e:
        print(f"[ERROR] {e}")

    return False


if __name__ == '__main__':
    print("="*50)
    print("ChromaDB Integration Test")
    print("="*50 + "\n")

    success = test_basic_chromadb()
    test_ollama_connection()

    if success:
        print("\n[INFO] ChromaDB is working correctly!")
        print("[INFO] You can now use the RAG system with ChromaDB")
        sys.exit(0)
    else:
        sys.exit(1)
