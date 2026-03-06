"""Tests for document loader"""

import pytest
import tempfile
from pathlib import Path

from zenpdf.loader import DocumentLoader


class TestDocumentLoader:
    def test_get_supported_extensions(self):
        """Test supported extensions list"""
        exts = DocumentLoader.get_supported_extensions()
        assert ".pdf" in exts
        assert ".docx" in exts
        assert ".txt" in exts

    def test_file_not_found(self):
        """Test loading non-existent file"""
        with pytest.raises(FileNotFoundError):
            DocumentLoader.load_file("nonexistent.pdf")

    def test_unsupported_file_type(self):
        """Test unsupported file type"""
        with pytest.raises(ValueError):
            DocumentLoader.load_file("test.xyz")

    def test_directory_not_found(self):
        """Test loading non-existent directory"""
        with pytest.raises(NotADirectoryError):
            DocumentLoader.load_directory("nonexistent_dir")
