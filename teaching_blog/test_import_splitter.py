# -*- coding: utf-8 -*-
"""Test pure_splitter import"""

print("Step 1: Import sys")
import sys
print("OK")

print("\nStep 2: Import from services.pure_splitter")
try:
    from services.pure_splitter import PurePythonTextSplitter, Document
    print("OK")
except Exception as e:
    print(f"FAIL: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nStep 3: Create splitter instance")
splitter = PurePythonTextSplitter(chunk_size=100, chunk_overlap=20)
print("OK")

print("\nStep 4: Test splitting")
text = "Hello world. This is a test. " * 20
chunks = splitter.split_text(text)
print(f"OK - Created {len(chunks)} chunks")

print("\nSUCCESS!")
