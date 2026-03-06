"""Ollama LLM wrapper"""

from typing import Iterator, Optional

from langchain_ollama import ChatOllama


class OllamaLLMWrapper:
    """Wrapper for Ollama chat model"""

    def __init__(
        self,
        model: str = "llama3.2:1b",
        temperature: float = 0.7,
        stream: bool = True,
    ):
        self.model = model
        self.temperature = temperature
        self.stream = stream
        self._llm = ChatOllama(
            model=model,
            temperature=temperature,
        )

    def generate(self, prompt: str) -> str:
        """Generate a non-streaming response"""
        response = self._llm.invoke(prompt)
        return response.content if hasattr(response, "content") else str(response)

    def stream_generate(self, prompt: str) -> Iterator[str]:
        """Generate a streaming response"""
        for chunk in self._llm.stream(prompt):
            yield chunk.content if hasattr(chunk, "content") else str(chunk)

    def update_params(self, model: str = None, temperature: float = None):
        """Update LLM parameters"""
        if model is not None:
            self.model = model
            self._llm = ChatOllama(model=model, temperature=self.temperature)
        if temperature is not None:
            self.temperature = temperature
            self._llm = ChatOllama(model=self.model, temperature=temperature)
