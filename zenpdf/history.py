"""Chat history management with file persistence"""

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Any


@dataclass
class ChatMessage:
    """A single chat message"""
    question: str
    answer: str
    sources: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class ChatHistory:
    """Manage chat history for RAG with file persistence"""

    def __init__(self, max_size: int = 50, history_path: str = None):
        self.max_size = max_size
        self.history_path = history_path or "./zenpdf_db/chat_history.json"
        self.messages: List[ChatMessage] = []
        self._load()

    def _ensure_dir(self):
        """Ensure the history file directory exists"""
        directory = os.path.dirname(self.history_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def _load(self) -> None:
        """Load history from file"""
        if os.path.exists(self.history_path):
            try:
                with open(self.history_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.messages = [ChatMessage(**msg) for msg in data.get("messages", [])]
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to load history: {e}")
                self.messages = []

    def _save(self) -> None:
        """Save history to file"""
        self._ensure_dir()
        try:
            data = {
                "generated_at": datetime.now().isoformat(),
                "messages": [asdict(msg) for msg in self.messages]
            }
            with open(self.history_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"Warning: Failed to save history: {e}")

    def add(self, question: str, answer: str, sources: List[Dict[str, Any]] = None):
        """Add a message to history"""
        msg = ChatMessage(question=question, answer=answer, sources=sources or [])
        self.messages.append(msg)
        
        if len(self.messages) > self.max_size:
            self.messages = self.messages[-self.max_size:]
        
        self._save()

    def get_history(self) -> List[ChatMessage]:
        """Get all messages"""
        return self.messages.copy()

    def get_formatted_history(self) -> str:
        """Get formatted history for prompt"""
        if not self.messages:
            return ""
        
        lines = []
        for msg in self.messages[-5:]:
            lines.append(f"User: {msg.question}")
            lines.append(f"Assistant: {msg.answer[:200]}...")
        
        return "\n".join(lines)

    def export_markdown(self) -> str:
        """Export history as markdown"""
        lines = [
            "# zenpdf Chat History",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            "",
        ]
        
        for i, msg in enumerate(self.messages, 1):
            lines.append(f"## Q{i}: {msg.question}")
            lines.append("")
            lines.append("**Answer:**")
            lines.append(msg.answer if msg.answer else "(Streaming response)")
            lines.append("")
            
            if msg.sources:
                sources_str = ", ".join([
                    s.get("metadata", {}).get("source", "unknown")
                    for s in msg.sources
                ])
                lines.append(f"**Sources:** {sources_str}")
                lines.append("")
            
            lines.append("---")
            lines.append("")
        
        return "\n".join(lines)

    def export_json(self) -> str:
        """Export history as JSON"""
        return json.dumps({
            "generated_at": datetime.now().isoformat(),
            "messages": [asdict(msg) for msg in self.messages]
        }, indent=2)

    def clear(self):
        """Clear all history"""
        self.messages = []
        self._save()

    def set_max_size(self, size: int):
        """Set maximum history size"""
        self.max_size = size
        if len(self.messages) > size:
            self.messages = self.messages[-size:]
        self._save()

    def __len__(self):
        return len(self.messages)
