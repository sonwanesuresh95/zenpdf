"""Chroma vector store management"""

import os
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional

import chromadb
from chromadb.config import Settings

from zenpdf.embedder import OllamaEmbedder


class VectorStore:
    """ChromaDB vector store for document retrieval"""

    def __init__(self, db_path: str, embed_model: str):
        self.db_path = db_path
        self.embed_model = embed_model

        Path(db_path).mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=db_path, settings=Settings(anonymized_telemetry=False)
        )

        self.embedder = OllamaEmbedder(model=embed_model)

        self.collection_name = "zenpdf_documents"
        self._collection = None

    @property
    def collection(self):
        """Get or create collection"""
        if self._collection is None:
            try:
                self._collection = self.client.get_collection(self.collection_name)
            except Exception:
                self._collection = self.client.create_collection(
                    self.collection_name, metadata={"hnsw:space": "cosine"}
                )
        return self._collection

    def add_documents(self, documents: List, ids: List[str] = None) -> List[str]:
        """Add documents to vector store"""
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in documents]

        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]

        embeddings = self.embedder.embed_documents(texts)

        self.collection.add(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)

        return ids

    def similarity_search(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        query_embedding = self.embedder.embed_query(query)

        results = self.collection.query(query_embeddings=[query_embedding], n_results=k)

        return [
            {
                "id": results["ids"][0][i],
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i] if "distances" in results else None,
            }
            for i in range(len(results["ids"][0]))
        ]

    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by its ID"""
        try:
            result = self.collection.get(ids=[doc_id])
            if result["ids"]:
                return {
                    "id": result["ids"][0],
                    "content": result["documents"][0],
                    "metadata": result["metadatas"][0],
                }
        except Exception:
            pass
        return None

    def list_documents(self) -> List[Dict[str, Any]]:
        """List all unique documents"""
        try:
            result = self.collection.get()
            docs = []
            seen_files = set()

            for i, metadata in enumerate(result["metadatas"]):
                source = metadata.get("source_file", "unknown")
                if source not in seen_files:
                    seen_files.add(source)
                    docs.append(
                        {
                            "id": result["ids"][i],
                            "source_file": source,
                            "metadata": metadata,
                        }
                    )
            return docs
        except Exception:
            return []

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document by ID"""
        try:
            self.collection.delete(ids=[doc_id])
            return True
        except Exception:
            return False

    def clear_all(self) -> None:
        """Clear all documents"""
        try:
            self.client.delete_collection(self.collection_name)
            self._collection = None
        except Exception:
            pass

    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        try:
            count = self.collection.count()
        except Exception:
            count = 0

        return {
            "db_path": self.db_path,
            "total_chunks": count,
            "embed_model": self.embed_model,
            "collection_name": self.collection_name,
        }

    def reset(self) -> None:
        """Reset the entire vector store"""
        self.clear_all()
