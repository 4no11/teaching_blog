# -*- coding: utf-8 -*-
"""
Step by step test of upload_documents internals
"""

import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '.')

from services.rag_service import RAGKnowledgeService

service = RAGKnowledgeService(provider='ollama')
kbs = service.list_knowledge_bases()
kb_id = kbs[0]['id']

print("Step 1: Check KB exists")
assert kb_id in service.metadata['knowledge_bases']
print("OK")

print("\nStep 2: Setup directories")
kb_info = service.metadata['knowledge_bases'][kb_id]
doc_dir = os.path.join(service.documents_dir, kb_id)
os.makedirs(doc_dir, exist_ok=True)
print(f"OK - {doc_dir}")

print("\nStep 3: Write test file")
test_file = os.path.join(doc_dir, 'step_test.txt')
with open(test_file, 'wb') as f:
    f.write(b"Hello world. This is a test.")
print("OK")

print("\nStep 4: Load document (pure Python)")
docs = service._load_document(test_file, 'step_test.txt')
if docs:
    print(f"OK - Loaded {len(docs)} doc(s)")
else:
    print("FAIL - No docs loaded")
    sys.exit(1)

print("\nStep 5: Check all_documents list")
all_documents = []
all_documents.extend(docs)
print(f"OK - {len(all_documents)} doc(s) in list")

print("\nStep 6: Update metadata")
service.metadata['knowledge_bases'][kb_id]['document_count'] += 1
service._save_metadata()
print("OK")

print("\nStep 7: Import pure splitter (this might crash!)")
try:
    from services.pure_splitter import PurePythonTextSplitter
    print("OK - Import successful")
except Exception as e:
    print(f"FAIL - {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nStep 8: Create splitter instance")
splitter = PurePythonTextSplitter(chunk_size=100, chunk_overlap=20)
print("OK")

print("\nStep 9: Split documents")
chunks = splitter.split_documents(all_documents)
print(f"OK - {len(chunks)} chunks created")

print("\nStep 10: Import chroma_compat")
from services.chroma_compat import PersistentClient
print("OK")

print("\nStep 11: Create ChromaDB client")
chroma_path = kb_info.get('chroma_path', os.path.join(service.chroma_dir, kb_id))
os.makedirs(chroma_path, exist_ok=True)
client = PersistentClient(path=chroma_path)
print("OK")

print("\nStep 12: Get or create collection")
collection = client.get_or_create_collection(
    "documents",
    embedding_function=None
)
print("OK")

print("\nStep 13: Add document to collection (without real embedding)")
collection.upsert(
    ids=["test_manual"],
    documents=[chunks[0].page_content],
    metadatas=[{"source": "test.txt"}],
    embeddings=[[0.1] * 768]  # Fake 768-dim vector
)
count = collection.count()
print(f"OK - Collection now has {count} items")

print("\n" + "="*60)
print("SUCCESS! All steps completed!")
print("="*60)
