from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        chunks = self.store.search(question, top_k=top_k)
        if not chunks:
            return "Không tìm thấy thông tin liên quan trong cơ sở tri thức."

        context_blocks: list[str] = []
        for idx, chunk in enumerate(chunks, start=1):
            context_blocks.append(f"[Đoạn {idx}]\n{chunk['content']}")
        context = "\n\n".join(context_blocks)

        prompt = (
            "Bạn là trợ lý trả lời dựa trên ngữ cảnh được cung cấp.\n"
            f"Ngữ cảnh:\n{context}\n\n"
            f"Câu hỏi: {question}\n"
            "Câu trả lời:"
        )
        return self.llm_fn(prompt)
