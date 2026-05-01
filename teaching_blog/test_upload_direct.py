# -*- coding: utf-8 -*-
"""
Direct test of upload_documents
"""

import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '.')

print("Test upload_documents directly")
print("="*60)

from services.rag_service import RAGKnowledgeService

service = RAGKnowledgeService(provider='ollama')

kbs = service.list_knowledge_bases()
if not kbs:
    print("No KB found, creating...")
    result = service.create_knowledge_base("direct_test", "Test")
    kb_id = result['knowledge_base']['id']
else:
    kb_id = kbs[0]['id']
    print(f"Using KB: {kbs[0]['name']}")

test_content = b"""This is a test document.
It has multiple lines.
Python is great for AI development."""

print(f"\nCalling upload_documents for KB: {kb_id[:20]}...")
print(f"Content length: {len(test_content)} bytes")

try:
    result = service.upload_documents(
        kb_id=kb_id,
        files=[('direct_test.txt', test_content)],
        chunk_size=100,
        chunk_overlap=20,
        skip_vectorization=False
    )

    print("\nResult:")
    print(f"  Success: {result.get('success')}")
    print(f"  Files: {result.get('uploaded_files')}")
    print(f"  Chunks: {result.get('total_chunks')}")
    print(f"  Message: {result.get('message')}")

    if not result.get('success'):
        print(f"\n  Error: {result.get('error')}")

except Exception as e:
    print(f"\nException: {e}")
    import traceback
    traceback.print_exc()

print("\nDone!")
