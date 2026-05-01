# -*- coding: utf-8 -*-
"""
Minimal ChromaDB test - find exact crash point
"""

import sys

print("Import chromadb...")
import chromadb
print("OK")

print("\nCreate client...")
client = chromadb.EphemeralClient()
print("OK")

print("\nCreate collection (no embedding_function param)...")
try:
    collection = client.create_collection("test2")
    print("OK")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

print("\nCollection count:", collection.count())
print("OK - basic operations work")

print("\n" + "="*50)
print("ChromaDB can be imported and initialized!")
print("Problem is in data operations (likely ONNX/NumPy DLL)")
