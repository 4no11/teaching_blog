# -*- coding: utf-8 -*-
"""
Step-by-step debug of RAG upload process
"""

import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '.')

print("="*60)
print("Debug RAG Upload Process")
print("="*60)

# Step 1: Import
print("\n[1] Import RAG service...")
from services.rag_service import RAGKnowledgeService
print("  OK")

# Step 2: Initialize
print("\n[2] Initialize service...")
service = RAGKnowledgeService(provider='ollama')
print(f"  OK - Provider: {service.provider}")

# Step 3: Get existing KB
print("\n[3] Get knowledge base...")
kbs = service.list_knowledge_bases()
if kbs:
    kb_id = kbs[0]['id']
    print(f"  OK - Using: {kbs[0]['name']} ({kb_id[:20]}...)")
else:
    print("  No KB found, creating...")
    result = service.create_knowledge_base("debug_test", "Test")
    if result['success']:
        kb_id = result['knowledge_base']['id']
        print(f"  OK - Created: {kb_id}")
    else:
        sys.exit(1)

# Step 4: Test document loading (pure Python)
print("\n[4] Test document loading (pure Python)...")
test_file = os.path.join(service.documents_dir, 'debug_test.txt')
with open(test_file, 'w', encoding='utf-8') as f:
    f.write("""This is a test document for debugging.
It contains multiple lines to test text splitting.
Python programming is fun and useful.""")

try:
    docs = service._load_document(test_file, 'debug_test.txt')
    if docs:
        print(f"  OK - Loaded {len(docs)} doc(s)")
        print(f"      Content length: {len(docs[0].page_content)} chars")
    else:
        print("  FAIL - No documents loaded")
        sys.exit(1)
except Exception as e:
    print(f"  FAIL - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 5: Test text splitting
print("\n[5] Test text splitting (pure Python)...")
try:
    from services.pure_splitter import PurePythonTextSplitter
    splitter = PurePythonTextSplitter(
        chunk_size=100,
        chunk_overlap=20,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(docs)
    print(f"  OK - Split into {len(chunks)} chunks")
    for i, chunk in enumerate(chunks[:3]):
        print(f"      Chunk {i}: {chunk.page_content[:50]}...")
except Exception as e:
    print(f"  FAIL - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 6: Test ChromaDB compat layer
print("\n[6] Test ChromaDB compatible layer...")
try:
    from services.chroma_compat import PersistentClient
    import tempfile

    temp_dir = tempfile.mkdtemp(prefix='chroma_debug_')
    client = PersistentClient(path=temp_dir)
    collection = client.get_or_create_collection(
        "documents",
        embedding_function=None
    )

    # Add a test vector (768-dim)
    collection.upsert(
        ids=["test_1"],
        documents=[chunks[0].page_content],
        metadatas=[{"source": "test.txt"}],
        embeddings=[[0.1] * 768]
    )
    count = collection.count()
    print(f"  OK - Added to ChromaDB compat layer, count={count}")

    # Query
    results = collection.query(
        query_embeddings=[[0.1] * 768],
        n_results=1
    )
    if results['documents'] and results['documents'][0]:
        print(f"  OK - Query works, result: {results['documents'][0][0][:40]}...")

    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)

except Exception as e:
    print(f"  FAIL - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("SUCCESS! All steps passed!")
print("="*60)
