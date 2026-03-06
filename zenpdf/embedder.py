"""Ollama embeddings wrapper"""

from typing import List

from langchain_ollama import OllamaEmbeddings as LangChainOllamaEmbeddings


class OllamaEmbedder:
    """Ollama embeddings for document and query embedding"""

    def __init__(self, model: str = "nomic-embed-text"):
        self.model = model
        self._embeddings = LangChainOllamaEmbeddings(model=model)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple documents"""
        return self._embeddings.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        return self._embeddings.embed_query(text)

    def update_model(self, model: str) -> None:
        """Update the embedding model"""
        self.model = model
        self._embeddings = LangChainOllamaEmbeddings(model=model)
