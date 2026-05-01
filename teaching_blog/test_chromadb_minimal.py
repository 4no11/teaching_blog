# -*- coding: utf-8 -*-
"""
Minimal ChromaDB test - check basic functionality
"""

import sys

print("Step 1: Import chromadb")
try:
    import chromadb
    print(f"  OK - version {chromadb.__version__}")
except Exception as e:
    print(f"  FAIL - {e}")
    sys.exit(1)

print("\nStep 2: Create ephemeral client (in-memory)")
try:
    client = chromadb.Client()
    print("  OK - Ephemeral client created")
except Exception as e:
    print(f"  FAIL - {e}")
    sys.exit(1)

print("\nStep 3: Create collection")
try:
    collection = client.create_collection("test")
    print("  OK - Collection created")
except Exception as e:
    print(f"  FAIL - {e}")
    sys.exit(1)

print("\nStep 4: Add documents (without embeddings)")
try:
    collection.add(
        ids=["1", "2"],
        documents=["hello", "world"]
    )
    count = collection.count()
    print(f"  OK - Added {count} documents")
except Exception as e:
    print(f"  FAIL - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nStep 5: Query collection")
try:
    results = collection.query(
        query_texts=["hello"],
        n_results=1
    )
    print(f"  OK - Query returned {len(results['documents'][0])} results")
except Exception as e:
    print(f"  FAIL - {e}")
    sys.exit(1)

print("\n" + "="*50)
print("SUCCESS! ChromaDB works correctly!")
print("="*50)
