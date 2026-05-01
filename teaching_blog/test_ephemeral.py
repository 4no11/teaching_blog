# -*- coding: utf-8 -*-
"""
Test ChromaDB EphemeralClient (in-memory)
"""

import sys

print("Test 1: EphemeralClient with embeddings")
print("-" * 40)

try:
    import chromadb
    client = chromadb.EphemeralClient()
    collection = client.create_collection(
        "test",
        embedding_function=None
    )

    # Add with manual embeddings
    collection.add(
        ids=["1"],
        documents=["test document"],
        embeddings=[[0.1]*768]
    )

    count = collection.count()
    print(f"OK - Added {count} document(s)")

    # Query
    results = collection.query(
        query_embeddings=[[0.1]*768],
        n_results=1
    )
    print(f"OK - Query works")

except Exception as e:
    print(f"FAIL - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*50)
print("SUCCESS!")
