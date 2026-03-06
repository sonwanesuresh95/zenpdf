"""Document loader for PDF, DOCX, and TXT files"""

import os
from pathlib import Path
from typing import List

from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
)

EXTENSION_LOADERS = {
    ".pdf": PyPDFLoader,
    ".docx": Docx2txtLoader,
    ".txt": TextLoader,
}


class DocumentLoader:
    """Load documents from various file formats"""

    @staticmethod
    def load_file(file_path: str) -> List:
        """Load a single file"""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = path.suffix.lower()

        if ext not in EXTENSION_LOADERS:
            raise ValueError(
                f"Unsupported file type: {ext}. Supported: {list(EXTENSION_LOADERS.keys())}"
            )

        loader_class = EXTENSION_LOADERS[ext]

        if ext == ".txt":
            loader = loader_class(str(path), encoding="utf-8")
        else:
            loader = loader_class(str(path))

        docs = loader.load()
        
        for doc in docs:
            doc.metadata["source_file"] = str(path)
        
        return docs

    @staticmethod
    def load_directory(dir_path: str) -> List:
        """Load all supported files from a directory"""
        path = Path(dir_path)

        if not path.is_dir():
            raise NotADirectoryError(f"Directory not found: {dir_path}")

        documents = []
        for ext in EXTENSION_LOADERS:
            for file_path in path.rglob(f"*{ext}"):
                try:
                    docs = DocumentLoader.load_file(str(file_path))
                    for doc in docs:
                        doc.metadata["source_file"] = str(file_path)
                    documents.extend(docs)
                except Exception as e:
                    print(f"Warning: Failed to load {file_path}: {e}")

        return documents

    @staticmethod
    def get_supported_extensions() -> List[str]:
        """Get list of supported file extensions"""
        return list(EXTENSION_LOADERS.keys())
