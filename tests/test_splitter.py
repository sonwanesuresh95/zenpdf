"""Tests for text splitter"""

import pytest

from zenpdf.splitter import TextSplitter


class TestTextSplitter:
    def test_default_params(self):
        """Test default parameters"""
        splitter = TextSplitter()
        assert splitter.chunk_size == 1000
        assert splitter.chunk_overlap == 100

    def test_custom_params(self):
        """Test custom parameters"""
        splitter = TextSplitter(chunk_size=500, chunk_overlap=50)
        assert splitter.chunk_size == 500
        assert splitter.chunk_overlap == 50

    def test_split_text(self):
        """Test text splitting"""
        splitter = TextSplitter(chunk_size=100, chunk_overlap=10)

        text = "This is a test. " * 50
        chunks = splitter.split_text(text)

        assert len(chunks) > 0
        assert all(isinstance(c, str) for c in chunks)

    def test_update_params(self):
        """Test updating parameters"""
        splitter = TextSplitter()
        splitter.update_params(chunk_size=500)

        assert splitter.chunk_size == 500
