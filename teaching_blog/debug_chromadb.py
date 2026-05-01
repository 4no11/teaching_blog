# -*- coding: utf-8 -*-
"""
Debug ChromaDB upload process
"""

import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '.')

print("Step 1: Import chromadb")
import chromadb
print(f"  OK - version {chromadb.__version__}")

print("\nStep 2: Create temp directory")
import tempfile
test_dir = tempfile.mkdtemp(prefix='chroma_debug_')
print(f"  OK - {test_dir}")

print("\nStep 3: Create PersistentClient with embedding_function=None")
try:
    client = chromadb.PersistentClient(path=test_dir)
    print("  OK - Client created")
except Exception as e:
    print(f"  FAIL - {e}")
    sys.exit(1)

print("\nStep 4: Create collection with embedding_function=None")
try:
    collection = client.get_or_create_collection(
        name="documents",
        metadata={"hnsw:space": "cosine"},
        embedding_function=None
    )
    print("  OK - Collection created (no default embedding)")
except Exception as e:
    print(f"  FAIL - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nStep 5: Add document WITH embeddings (manual)")
try:
    collection.upsert(
        ids=["doc1"],
        documents=["This is a test document about Python programming"],
        metadatas=[{"source": "test.txt"}],
        embeddings=[[0.1, 0.2, 0.3] * 256]  # 768-dim vector
    )
    count = collection.count()
    print(f"  OK - Added document, total={count}")
except Exception as e:
    print(f"  FAIL - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nStep 6: Query WITH embedding vector")
try:
    results = collection.query(
        query_embeddings=[[0.1, 0.2, 0.3] * 256],
        n_results=1,
        include=['documents', 'metadatas', 'distances']
    )

    if results['documents'] and results['documents'][0]:
        print(f"  OK - Query returned {len(results['documents'][0])} result(s)")
        print(f"  Document: {results['documents'][0][0][:60]}...")
        print(f"  Distance: {results['distances'][0][0]}")
    else:
        print("  WARN - No results")
except Exception as e:
    print(f"  FAIL - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Cleanup
import shutil
shutil.rmtree(test_dir)
print("\n  Cleanup completed")

print("\n" + "="*50)
print("SUCCESS! ChromaDB works with manual embeddings!")
print("="*50)
