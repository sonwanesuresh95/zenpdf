"""Configuration management for zenpdf"""

import json
import os
from pathlib import Path
from typing import Any

DEFAULT_CONFIG = {
    "model": "llama3.1:1b",
    "embed_model": "nomic-embed-text",
    "chunk_size": 1000,
    "chunk_overlap": 100,
    "k": 4,
    "db_path": "./zenpdf_db",
    "temperature": 0.7,
    "stream": True,
    "history_size": 50,
    "history_path": "./zenpdf_db/chat_history.json",
}


class Config:
    """Configuration manager for zenpdf"""

    def __init__(self, config_path: str | None = None):
        self.config_path = config_path or os.path.join(os.getcwd(), ".zenpdf_config.json")
        self._config = DEFAULT_CONFIG.copy()
        self._load()

    def _load(self) -> None:
        """Load config from file if exists"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    user_config = json.load(f)
                    self._config.update(user_config)
            except (json.JSONDecodeError, IOError):
                pass

    def save(self) -> None:
        """Save current config to file"""
        with open(self.config_path, "w") as f:
            json.dump(self._config, f, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        """Get config value"""
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set config value"""
        self._config[key] = value

    def update(self, **kwargs) -> None:
        """Update multiple config values"""
        self._config.update(kwargs)

    @property
    def all(self) -> dict:
        """Get all config as dict"""
        return self._config.copy()

    def reset(self) -> None:
        """Reset to default config"""
        self._config = DEFAULT_CONFIG.copy()
