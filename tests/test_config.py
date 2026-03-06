"""Tests for config module"""

import pytest
import os
import tempfile
from pathlib import Path

from zenpdf.config import Config, DEFAULT_CONFIG


class TestConfig:
    def test_default_config(self):
        """Test default configuration values"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(config_path=os.path.join(tmpdir, "test_config.json"))

            for key, value in DEFAULT_CONFIG.items():
                assert config.get(key) == value

    def test_get_set(self):
        """Test get and set methods"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(config_path=os.path.join(tmpdir, "test_config.json"))

            config.set("model", "llama3.2:1b")
            assert config.get("model") == "llama3.2:1b"

    def test_update(self):
        """Test update method"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(config_path=os.path.join(tmpdir, "test_config.json"))

            config.update(chunk_size=500, k=8)
            assert config.get("chunk_size") == 500
            assert config.get("k") == 8

    def test_save_load(self):
        """Test save and load"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "test_config.json")

            config1 = Config(config_path=config_path)
            config1.set("model", "llama3.2:1b")
            config1.save()

            config2 = Config(config_path=config_path)
            assert config2.get("model") == "llama3.2:1b"

    def test_reset(self):
        """Test reset method"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(config_path=os.path.join(tmpdir, "test_config.json"))

            config.set("model", "llama3.2:1b")
            config.reset()

            assert config.get("model") == DEFAULT_CONFIG["model"]
