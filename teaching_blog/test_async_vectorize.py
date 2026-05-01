# -*- coding: utf-8 -*-
"""
测试异步向量化系统
"""

import os
import sys
import time
import threading

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '.')

print("="*60)
print("测试异步向量化系统")
print("="*60)

# 1. 初始化服务
print("\n[1] 初始化RAG服务...")
from services.rag_service import RAGKnowledgeService
service = RAGKnowledgeService(provider='ollama')
print(f"  OK - Provider: {service.provider}")

# 2. 获取知识库
print("\n[2] 获取知识库...")
kbs = service.list_knowledge_bases()
if not kbs:
    print("  没有知识库，创建测试用...")
    result = service.create_knowledge_base("async_test", "Async test")
    kb_id = result['knowledge_base']['id']
else:
    kb_id = kbs[0]['id']
    print(f"  OK - 使用: {kbs[0]['name']}")

# 3. 上传文档（快速模式，不向量化）
print("\n[3] 上传测试文档...")
test_content = b"""Asynchronous Vectorization Test
=====================================

This document will be vectorized asynchronously in the background.

Key points:
- The vectorization runs in a separate thread
- Progress is tracked in real-time
- User can check progress via API
- No timeout issues!

Python is great for AI applications.
ChromaDB stores vectors efficiently.
Ollama generates embeddings locally."""

result = service.upload_documents(
    kb_id=kb_id,
    files=[('async_test.txt', test_content)],
    skip_vectorization=True  # 快速保存，稍后向量化
)

if result.get('success'):
    print(f"  OK - 文档已上传")
    print(f"      文件数: {len(result['uploaded_files'])}")
else:
    print(f"  FAIL - {result.get('error')}")
    sys.exit(1)

# 4. 测试异步向量化
print("\n[4] 启动异步向量化任务...")

from services.vectorization_progress import get_progress_tracker
progress_tracker = get_progress_tracker()

# 模拟后台线程执行向量化
def async_vectorize():
    """模拟异步向量化"""
    try:
        print("  [后台线程] 开始向量化...")

        # 重新读取文件并执行完整向量化
        documents = service.get_documents(kb_id)
        files = []
        doc_dir = os.path.join(service.documents_dir, kb_id)
        for doc in documents:
            filepath = os.path.join(doc_dir, doc['filename'])
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    content = f.read()
                files.append((doc['filename'], content))

        if files:
            result = service.upload_documents(
                kb_id=kb_id,
                files=files,
                chunk_size=100,
                chunk_overlap=20,
                skip_vectorization=False  # 执行向量化
            )
            print(f"  [后台线程] 向量化完成: {result.get('success')}")
        else:
            print("  [后台线程] 没有找到文件")
            progress_tracker.fail_task(kb_id, "没有可向量化的文件")

    except Exception as e:
        print(f"  [后台线程] 向量化失败: {e}")
        import traceback
        traceback.print_exc()
        progress_tracker.fail_task(kb_id, str(e))

# 初始化进度
progress_tracker.start_task(kb_id, total_chunks=0)

# 启动后台线程
thread = threading.Thread(target=async_vectorize, name="test-vectorize", daemon=True)
thread.start()
print(f"  OK - 后台任务已启动 (Thread: {thread.name})")

# 5. 轮询进度（模拟前端行为）
print("\n[5] 轮询进度（模拟前端）...")
print("-"*40)

max_wait = 120  # 最多等待2分钟
start_time = time.time()
completed = False

while time.time() - start_time < max_wait:
    # 每2秒查询一次
    time.sleep(2)

    progress = progress_tracker.get_progress(kb_id)
    if not progress:
        print("  [WARN] 未找到进度信息")
        continue

    status = progress.get('status')
    percent = progress.get('progress_percent', 0)
    message = progress.get('message', '')
    current = progress.get('current_chunk', 0)
    total = progress.get('total_chunks', 0)

    print(f"  [{percent:3d}%] {message}")

    if status == 'completed':
        completed = True
        print("\n  *** 向量化完成! ***")
        break
    elif status == 'failed':
        error = progress.get('error', '未知错误')
        print(f"\n  !!! 向量化失败: {error} !!!")
        break

if not completed:
    elapsed = int(time.time() - start_time)
    print(f"\n  [TIMEOUT] 等待了 {elapsed} 秒仍未完成")

# 6. 验证结果
print("\n[6] 验证ChromaDB存储...")
try:
    from services.chroma_compat import PersistentClient

    chroma_path = service.metadata['knowledge_bases'][kb_id].get('chroma_path')
    if chroma_path and os.path.exists(chroma_path):
        client = PersistentClient(path=chroma_path)
        collection = client.get_collection("documents")
        count = collection.count()
        print(f"  OK - ChromaDB中有 {count} 个文档")
    else:
        print("  WARN - ChromaDB路径不存在")
except Exception as e:
    print(f"  ERROR - {e}")

# 清理
print("\n[7] 清理...")
progress_tracker.clear_task(kb_id)
print("  OK")

print("\n" + "="*60)
if completed:
    print("[SUCCESS] 异步向量化系统工作正常!")
else:
    print("[PARTIAL] 进度追踪正常，但向量化可能未完成")
print("="*60)

print("\n使用说明:")
print("  1. 重启Flask应用: python app.py")
print("  2. 访问 http://localhost:5000/rag-knowledge")
print("  3. 点击'开始向量化'按钮")
print("  4. 观察实时进度（不再超时！）")
print("  5. 完成后自动提示")
