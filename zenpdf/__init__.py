"""zenpdf - Serene local PDF Q&A with RAG"""

__version__ = "0.1.0"
__author__ = "Your Name"

from zenpdf.config import Config, DEFAULT_CONFIG
from zenpdf.loader import DocumentLoader
from zenpdf.splitter import TextSplitter
from zenpdf.vectorstore import VectorStore
from zenpdf.embedder import OllamaEmbedder
from zenpdf.llm import OllamaLLMWrapper
from zenpdf.rag import RAGChain
from zenpdf.history import ChatHistory

__all__ = [
    "Config",
    "DEFAULT_CONFIG",
    "DocumentLoader",
    "TextSplitter",
    "VectorStore",
    "OllamaEmbedder",
    "OllamaLLMWrapper",
    "RAGChain",
    "ChatHistory",
]
