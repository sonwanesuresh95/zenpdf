"""Tests for history module"""

import pytest
from datetime import datetime

from zenpdf.history import ChatHistory, ChatMessage


class TestChatHistory:
    def test_default_max_size(self):
        """Test default max size"""
        history = ChatHistory()
        assert history.max_size == 50

    def test_custom_max_size(self):
        """Test custom max size"""
        history = ChatHistory(max_size=10)
        assert history.max_size == 10

    def test_add_message(self):
        """Test adding messages"""
        history = ChatHistory()
        history.add("What is AI?", "AI is artificial intelligence.")

        assert len(history) == 1
        assert history.messages[0].question == "What is AI?"

    def test_max_size_enforcement(self):
        """Test max size is enforced"""
        history = ChatHistory(max_size=3)

        for i in range(5):
            history.add(f"Question {i}", f"Answer {i}")

        assert len(history) == 3

    def test_clear(self):
        """Test clearing history"""
        history = ChatHistory()
        history.add("Q1", "A1")
        history.add("Q2", "A2")

        history.clear()

        assert len(history) == 0

    def test_export_markdown(self):
        """Test markdown export"""
        history = ChatHistory()
        history.add("What is AI?", "AI is artificial intelligence.")

        md = history.export_markdown()

        assert "# zenpdf Chat History" in md
        assert "What is AI?" in md

    def test_export_json(self):
        """Test JSON export"""
        history = ChatHistory()
        history.add("What is AI?", "AI is artificial intelligence.")

        json_str = history.export_json()

        assert '"question": "What is AI?"' in json_str

    def test_set_max_size(self):
        """Test setting max size"""
        history = ChatHistory(max_size=50)

        for i in range(30):
            history.add(f"Q{i}", f"A{i}")

        history.set_max_size(5)

        assert history.max_size == 5
        assert len(history) == 5
