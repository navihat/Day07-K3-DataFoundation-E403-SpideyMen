from typing import Callable

from .store import EmbeddingStore

NO_CONTEXT_ANSWER = "Không tìm thấy thông tin liên quan trong cơ sở tri thức."

PROMPT_TEMPLATE = """Bạn là trợ lý trả lời câu hỏi dựa trên tài liệu được cung cấp.

Chỉ dùng thông tin trong phần NGỮ CẢNH dưới đây để trả lời. Nếu ngữ cảnh không đủ
thông tin, hãy nói rõ là không tìm thấy thay vì suy đoán. Trích dẫn nguồn khi có.

NGỮ CẢNH:
{context}

CÂU HỎI: {question}

TRẢ LỜI:"""


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
        results = self.store.search(question, top_k=top_k)
        if not results:
            return NO_CONTEXT_ANSWER

        blocks = []
        for index, result in enumerate(results, start=1):
            metadata = result.get("metadata") or {}
            source = metadata.get("source_url") or metadata.get("source") or metadata.get("doc_id", "unknown")
            blocks.append(
                f"[{index}] (nguồn: {source} | score: {result['score']:.3f})\n{result['content']}"
            )

        prompt = PROMPT_TEMPLATE.format(context="\n\n".join(blocks), question=question)
        return self.llm_fn(prompt)
