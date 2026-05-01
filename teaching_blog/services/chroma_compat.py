# -*- coding: utf-8 -*-
"""
ChromaDB Compatible Vector Store - Pure Python Implementation

This module provides a ChromaDB-compatible API using pure Python,
avoiding DLL loading issues with ONNX/PyTorch/NumPy.

Usage:
    from chroma_compat import PersistentClient

    client = PersistentClient(path='./my_vector_db')
    collection = client.get_or_create_collection("documents")
    collection.add(ids=['1'], documents=['hello'], embeddings=[[0.1]*768])
    results = collection.query(query_embeddings=[[0.1]*768], n_results=1)
"""

import os
import json
import pickle
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)


class Collection:
    """ChromaDB-compatible Collection implementation"""

    def __init__(self, name: str, path: Path, metadata: Dict = None):
        self.name = name
        self.path = path / name
        self.metadata = metadata or {}
        self._ensure_dir()

    def _ensure_dir(self):
        """Ensure collection directory exists"""
        self.path.mkdir(parents=True, exist_ok=True)

        # Data files
        self.data_file = self.path / 'data.json'
        self.embeddings_file = self.path / 'embeddings.pkl'

        # Initialize if not exists
        if not self.data_file.exists():
            self._save_data({
                'ids': [],
                'documents': [],
                'metadatas': [],
                'embeddings': []
            })

    def _load_data(self) -> Dict:
        """Load data from disk"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                text_data = json.load(f)

            # Load embeddings separately
            embeddings = []
            if self.embeddings_file.exists():
                with open(self.embeddings_file, 'rb') as f:
                    embeddings = pickle.load(f)

            return {
                'ids': text_data.get('ids', []),
                'documents': text_data.get('documents', []),
                'metadatas': text_data.get('metadatas', []),
                'embeddings': embeddings
            }
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return {'ids': [], 'documents': [], 'metadatas': [], 'embeddings': []}

    def _save_data(self, data: Dict):
        """Save data to disk"""
        # Save text data as JSON
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump({
                'ids': data['ids'],
                'documents': data['documents'],
                'metadatas': data['metadatas']
            }, f, ensure_ascii=False, indent=2)

        # Save embeddings as binary (more efficient)
        with open(self.embeddings_file, 'wb') as f:
            pickle.dump(data['embeddings'], f)

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        import math

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def add(
        self,
        ids: List[str],
        documents: List[str] = None,
        metadatas: List[Dict] = None,
        embeddings: List[List[float]] = None
    ):
        """Add documents to collection"""
        data = self._load_data()

        # Validate inputs
        n = len(ids)
        if documents is None:
            documents = [None] * n
        if metadatas is None:
            metadatas = [None] * n
        if embeddings is None:
            embeddings = [None] * n

        # Append new data
        data['ids'].extend(ids)
        data['documents'].extend(documents)
        data['metadatas'].extend(metadatas)
        data['embeddings'].extend(embeddings)

        self._save_data(data)
        logger.info(f"Added {n} documents to {self.name}")

    def upsert(
        self,
        ids: List[str],
        documents: List[str] = None,
        metadatas: List[Dict] = None,
        embeddings: List[List[float]] = None
    ):
        """Add or update documents in collection"""
        data = self._load_data()

        # Validate inputs
        n = len(ids)
        if documents is None:
            documents = [None] * n
        if metadatas is None:
            metadatas = [None] * n
        if embeddings is None:
            embeddings = [None] * n

        # Upsert: update existing, add new
        id_set = set(data['ids'])
        for i, doc_id in enumerate(ids):
            if doc_id in id_set:
                # Update existing
                idx = data['ids'].index(doc_id)
                data['documents'][idx] = documents[i]
                data['metadatas'][idx] = metadatas[i]
                data['embeddings'][idx] = embeddings[i]
            else:
                # Add new
                data['ids'].append(doc_id)
                data['documents'].append(documents[i])
                data['metadatas'].append(metadatas[i])
                data['embeddings'].append(embeddings[i])

        self._save_data(data)
        logger.info(f"Upserted {n} documents to {self.name}")

    def query(
        self,
        query_texts: List[str] = None,
        query_embeddings: List[List[float]] = None,
        n_results: int = 10,
        include: List[str] = ['documents', 'metadatas', 'distances']
    ) -> Dict:
        """Query the collection for similar documents"""
        data = self._load_data()

        if not data['ids'] or not any(emb for emb in data['embeddings']):
            return {
                'ids': [[]],
                'documents': [[]] if 'documents' in include else None,
                'metadatas': [[]] if 'metadatas' in include else None,
                'distances': [[]] if 'distances' in include else None
            }

        # Use provided embeddings or generate placeholder
        if query_embeddings and query_embeddings[0]:
            query_vec = query_embeddings[0]
        else:
            # Return first n_results if no query vector
            result_indices = list(range(min(n_results, len(data['ids']))))
            return self._format_results(data, result_indices, include)

        # Calculate similarities
        similarities = []
        for i, emb in enumerate(data['embeddings']):
            if emb:
                sim = self._cosine_similarity(query_vec, emb)
                similarities.append((i, sim))

        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Get top k results
        top_k = similarities[:n_results]
        result_indices = [idx for idx, sim in top_k]

        return self._format_results(data, result_indices, include, similarities=top_k)

    def _format_results(
        self,
        data: Dict,
        indices: List[int],
        include: List[str],
        similarities: List = None
    ) -> Dict:
        """Format query results"""
        result = {'ids': [[data['ids'][i] for i in indices]]}

        if 'documents' in include:
            result['documents'] = [[data['documents'][i] for i in indices]]

        if 'metadatas' in include:
            result['metadatas'] = [[data['metadatas'][i] for i in indices]]

        if 'distances' in include and similarities:
            # Convert similarity to distance (1 - similarity)
            distances = [(1 - sim) for idx, sim in similarities[:len(indices)]]
            result['distances'] = [distances]
        elif 'distances' in include:
            result['distances'] = [[0.0] * len(indices)]

        return result

    def get(self, **kwargs) -> Dict:
        """Get documents from collection"""
        data = self._load_data()

        limit = kwargs.get('limit', None)
        ids = kwargs.get('ids', None)
        where = kwargs.get('where', None)

        # Filter
        if ids:
            indices = [i for i, id_ in enumerate(data['ids']) if id_ in ids]
        elif limit:
            indices = list(range(min(limit, len(data['ids']))))
        else:
            indices = list(range(len(data['ids'])))

        return {
            'ids': [data['ids'][i] for i in indices],
            'documents': [data['documents'][i] for i in indices],
            'metadatas': [data['metadatas'][i] for i in indices],
            'embeddings': [data['embeddings'][i] for i in indices]
        }

    def count(self) -> int:
        """Count documents in collection"""
        data = self._load_data()
        return len(data['ids'])

    def peek(self, limit: int = 10) -> Dict:
        """Peek at first few documents"""
        return self.get(limit=limit)

    def delete(self, ids: List[str] = None):
        """Delete documents by IDs"""
        if not ids:
            return

        data = self._load_data()
        id_set = set(ids)

        # Filter out deleted items
        new_data = {
            'ids': [],
            'documents': [],
            'metadatas': [],
            'embeddings': []
        }

        for i, doc_id in enumerate(data['ids']):
            if doc_id not in id_set:
                new_data['ids'].append(doc_id)
                new_data['documents'].append(data['documents'][i])
                new_data['metadatas'].append(data['metadatas'][i])
                new_data['embeddings'].append(data['embeddings'][i])

        self._save_data(new_data)
        logger(f"Deleted {len(ids)} documents from {self.name}")

    def modify(self, **kwargs):
        """Modify collection properties"""
        pass  # Not implemented for simplicity


class PersistentClient:
    """
    ChromaDB-compatible Persistent Client (Pure Python)

    Provides the same API as chromadb.PersistentClient but uses pure Python
    file storage instead of the native ChromaDB implementation.
    """

    def __init__(self, path: str):
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)
        self._collections: Dict[str, Collection] = {}
        logger.info(f"Initialized ChromaDB-compatible client at {path}")

    def get_or_create_collection(
        self,
        name: str,
        metadata: Dict = None,
        embedding_function=None  # Accepted but ignored
    ) -> Collection:
        """Get or create a collection"""
        if name in self._collections:
            return self._collections[name]

        collection = Collection(name=name, path=self.path, metadata=metadata)
        self._collections[name] = collection
        return collection

    def get_collection(self, name: str) -> Collection:
        """Get an existing collection"""
        if name not in self._collections:
            collection = Collection(name=name, path=self.path)
            self._collections[name] = collection
        return self._collections[name]

    def create_collection(self, name: str, **kwargs) -> Collection:
        """Create a new collection"""
        return self.get_or_create_collection(name, **kwargs)

    def list_collections(self) -> List:
        """List all collections"""
        collections = []
        if self.path.exists():
            for item in self.path.iterdir():
                if item.is_dir() and (item / 'data.json').exists():
                    collections.append(item.name)
        return collections

    def delete_collection(self, name: str):
        """Delete a collection"""
        col_path = self.path / name
        if col_path.exists():
            shutil.rmtree(col_path)
        if name in self._collections:
            del self._collections[name]


class EphemeralClient:
    """In-memory client (for compatibility)"""

    def __init__(self):
        import tempfile
        self.temp_dir = tempfile.mkdtemp(prefix='chroma_ephemeral_')
        self.client = PersistentClient(path=self.temp_dir)

    def get_or_create_collection(self, name: str, **kwargs) -> Collection:
        return self.client.get_or_create_collection(name, **kwargs)

    def create_collection(self, name: str, **kwargs) -> Collection:
        return self.client.create_collection(name, **kwargs)

    def get_collection(self, name: str) -> Collection:
        return self.client.get_collection(name)


def test_chroma_compat():
    """Test the ChromaDB-compatible implementation"""
    print("="*60)
    print("Testing ChromaDB-Compatible Vector Store")
    print("="*60)

    import tempfile
    test_dir = tempfile.mkdtemp(prefix='test_compat_')

    # Test 1: Create client and collection
    print("\n[1] Creating client and collection...")
    client = PersistentClient(path=test_dir)
    collection = client.get_or_create_collection(
        "test_docs",
        embedding_function=None
    )
    print("   OK")

    # Test 2: Add documents
    print("\n[2] Adding documents with embeddings...")
    collection.upsert(
        ids=["doc1", "doc2", "doc3"],
        documents=[
            "Python is a programming language",
            "ChromaDB is a vector database",
            "Machine learning is a subset of AI"
        ],
        metadatas=[{"source": "a"}, {"source": "b"}, {"source": "c"}],
        embeddings=[[0.1]*768, [0.2]*768, [0.3]*768]
    )
    count = collection.count()
    print(f"   OK - Added {count} documents")

    # Test 3: Query
    print("\n[3] Querying collection...")
    results = collection.query(
        query_embeddings=[[0.15]*768],
        n_results=2,
        include=['documents', 'metadatas', 'distances']
    )

    print(f"   OK - Found {len(results['ids'][0])} results:")
    for i, (doc, dist) in enumerate(zip(results['documents'][0], results['distances'][0])):
        print(f"      {i+1}. {doc[:50]}... (distance: {dist:.4f})")

    # Test 4: Get/Peek
    print("\n[4] Testing peek()...")
    sample = collection.peek(limit=1)
    print(f"   OK - First document: {sample['documents'][0][:40]}...")

    # Cleanup
    shutil.rmtree(test_dir)
    print("\n[5] Cleanup completed")

    print("\n" + "="*60)
    print("SUCCESS! All tests passed!")
    print("="*60)
    return True


if __name__ == '__main__':
    test_chroma_compat()
