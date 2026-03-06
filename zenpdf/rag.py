"""RAG chain for question answering"""

from typing import Iterator, List, Dict, Any

from zenpdf.vectorstore import VectorStore
from zenpdf.llm import OllamaLLMWrapper
from zenpdf.history import ChatHistory


class RAGChain:
    """Retrieval-Augmented Generation chain"""

    def __init__(
        self,
        vectorstore: VectorStore,
        llm: OllamaLLMWrapper,
        chat_history: ChatHistory,
        k: int = 4,
        stream: bool = True,
    ):
        self.vectorstore = vectorstore
        self.llm = llm
        self.chat_history = chat_history
        self.k = k
        self.stream = stream

    def _build_prompt(self, query: str, context_docs: List[Dict[str, Any]]) -> str:
        """Build prompt with context and history"""
        context = "\n\n".join(
            [
                f"Source {i + 1} ({doc['metadata'].get('source_file', 'unknown')}):\n{doc['content']}"
                for i, doc in enumerate(context_docs)
            ]
        )

        history_text = self.chat_history.get_formatted_history()

        prompt = f"""You are a helpful AI assistant answering questions about documents.
                    Your task is to provide accurate, detailed answers based ONLY on the provided context.

                    Chat History:
                    {history_text if history_text else "No previous messages"}

                    Context from documents:
                    {context}

                    Question: {query}

                    Instructions:
                    1. Answer based ONLY on the provided context
                    2. If the answer is not in the context, say "I don't have enough information to answer that question based on the provided documents."
                    3. Be concise but thorough
                    4. Reference the sources when possible

                    Answer:"""

        return prompt

    def ask(self, query: str, k: int = None) -> Dict[str, Any]:
        """Ask a question and get response"""
        k = k or self.k

        context_docs = self.vectorstore.similarity_search(query, k=k)

        if not context_docs:
            return {
                "answer": "No relevant documents found. Please index some documents first.",
                "sources": [],
            }

        prompt = self._build_prompt(query, context_docs)

        if self.stream:
            return {
                "answer": prompt,
                "sources": context_docs,
                "stream": True,
            }
        else:
            answer = self.llm.generate(prompt)
            return {
                "answer": answer,
                "sources": context_docs,
                "stream": False,
            }

    def stream_ask(self, query: str, k: int = None) -> Iterator[str]:
        """Ask question with streaming response"""
        k = k or self.k

        context_docs = self.vectorstore.similarity_search(query, k=k)

        if not context_docs:
            yield "No relevant documents found. Please index some documents first."
            return

        prompt = self._build_prompt(query, context_docs)

        for chunk in self.llm.stream_generate(prompt):
            yield chunk

        final_answer = ""
        self.chat_history.add(query, final_answer, context_docs)

    def update_params(self, k: int = None, stream: bool = None):
        """Update RAG parameters"""
        if k is not None:
            self.k = k
        if stream is not None:
            self.stream = stream
