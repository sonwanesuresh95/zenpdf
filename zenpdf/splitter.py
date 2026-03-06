"""Text splitting utilities"""

from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter


class TextSplitter:
    """Split documents into chunks for embedding"""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len,
        )

    def split_documents(self, documents: List) -> List:
        """Split documents into chunks"""
        return self._splitter.split_documents(documents)

    def split_text(self, text: str) -> List[str]:
        """Split text into chunks"""
        return self._splitter.split_text(text)

    def update_params(self, chunk_size: int = None, chunk_overlap: int = None):
        """Update splitting parameters"""
        if chunk_size is not None:
            self.chunk_size = chunk_size
        if chunk_overlap is not None:
            self.chunk_overlap = chunk_overlap

        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len,
        )
