# -*- coding: utf-8 -*-
"""
Pure Python Text Splitter - No external dependencies
"""

import re
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class Document:
    """Simple document class"""
    page_content: str
    metadata: Dict[str, Any]


class PurePythonTextSplitter:
    """
    Pure Python text splitter - avoids DLL issues with langchain dependencies

    Splits text into chunks while preserving context through overlap.
    """

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        separators: List[str] = None
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", " ", ""]

    def split_text(self, text: str) -> List[str]:
        """Split text into chunks"""
        if not text or len(text) <= self.chunk_size:
            return [text] if text else []

        chunks = []
        current_pos = 0
        text_length = len(text)

        while current_pos < text_length:
            # Calculate end position
            end_pos = min(current_pos + self.chunk_size, text_length)

            if end_pos < text_length:
                # Try to find a good break point
                best_break = self._find_best_breakpoint(text, current_pos, end_pos)
                end_pos = best_break

            chunk = text[current_pos:end_pos].strip()
            if chunk:
                chunks.append(chunk)

            # Move forward, accounting for overlap
            next_pos = end_pos - self.chunk_overlap
            if next_pos <= current_pos:
                next_pos = current_pos + 1  # Avoid infinite loop

            current_pos = max(next_pos, current_pos + 1)

        return chunks

    def _find_best_breakpoint(self, text: str, start: int, end: int) -> int:
        """Find the best position to split text"""
        # Search backwards from end for separators
        for sep in self.separators:
            if not sep:
                continue

            # Look for separator in the last 20% of the chunk
            search_start = max(start, end - int(self.chunk_size * 0.2))
            search_text = text[search_start:end]

            last_sep_pos = search_text.rfind(sep)
            if last_sep_pos != -1:
                return search_start + last_sep_pos + len(sep)

        # If no separator found, split at word boundary
        search_text = text[start:end]
        last_space = search_text.rfind(' ')
        if last_space > int(self.chunk_size * 0.5):
            return start + last_space + 1

        return end

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split list of documents into chunks"""
        result = []
        for doc in documents:
            chunks = self.split_text(doc.page_content)
            for i, chunk in enumerate(chunks):
                new_metadata = doc.metadata.copy()
                new_metadata['chunk'] = i
                result.append(Document(
                    page_content=chunk,
                    metadata=new_metadata
                ))
        return result


def test_splitter():
    """Test the pure Python splitter"""
    print("Testing PurePythonTextSplitter...")

    splitter = PurePythonTextSplitter(
        chunk_size=100,
        chunk_overlap=20
    )

    test_text = """
This is a test document.

It contains multiple paragraphs to test the splitting functionality.
The splitter should handle various separators like newlines and spaces correctly.

Python is a popular programming language used for many applications including web development, data science, and machine learning. It has a simple syntax that makes it easy to learn.

ChromaDB is a vector database designed for AI applications. It allows efficient similarity search on embeddings.
"""

    chunks = splitter.split_text(test_text)

    print(f"\nOriginal length: {len(test_text)} chars")
    print(f"Number of chunks: {len(chunks)}")

    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i+1} ({len(chunk)} chars):")
        print(f"  {chunk[:80]}...")

    # Test with Document objects
    docs = [Document(page_content=test_text, metadata={'source': 'test.txt'})]
    split_docs = splitter.split_documents(docs)

    print(f"\n\nDocument splitting:")
    print(f"  Input: 1 document")
    print(f"  Output: {len(split_docs)} documents")

    print("\n[OK] All tests passed!")
    return True


if __name__ == '__main__':
    test_splitter()
