from __future__ import annotations

import math
import re


class FixedSizeChunker:
    """
    Split text into fixed-size chunks with optional overlap.

    Rules:
        - Each chunk is at most chunk_size characters long.
        - Consecutive chunks share overlap characters.
        - The last chunk contains whatever remains.
        - If text is shorter than chunk_size, return [text].
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        step = self.chunk_size - self.overlap
        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks


class SentenceChunker:
    """
    Split text into chunks of at most max_sentences_per_chunk sentences.

    Sentence detection: split on ". ", "! ", "? " or ".\n".
    Strip extra whitespace from each chunk.
    """

    SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+")

    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        sentences = [s.strip() for s in self.SENTENCE_BOUNDARY.split(text.strip())]
        sentences = [s for s in sentences if s]

        chunks: list[str] = []
        for start in range(0, len(sentences), self.max_sentences_per_chunk):
            group = sentences[start : start + self.max_sentences_per_chunk]
            chunks.append(" ".join(group))
        return chunks


class RecursiveChunker:
    """
    Recursively split text using separators in priority order.

    Default separator priority:
        ["\n\n", "\n", ". ", " ", ""]
    """

    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        return self._split(text, list(self.separators))

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        text = current_text.strip()

        # Base cases: nothing left, or the piece already fits.
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        # No separator left (or the "" separator): hard cut at chunk_size.
        if not remaining_separators or remaining_separators[0] == "":
            pieces = [text[i : i + self.chunk_size].strip() for i in range(0, len(text), self.chunk_size)]
            return [p for p in pieces if p]

        separator, rest = remaining_separators[0], remaining_separators[1:]
        parts = text.split(separator)
        if len(parts) == 1:
            # Separator absent — try the next one in priority order.
            return self._split(text, rest)

        # Greedily merge parts back together while they still fit in chunk_size.
        chunks: list[str] = []
        buffer = ""
        for part in parts:
            candidate = part if not buffer else buffer + separator + part
            if len(candidate) <= self.chunk_size:
                buffer = candidate
                continue
            if buffer:
                chunks.append(buffer)
                buffer = ""
            if len(part) <= self.chunk_size:
                buffer = part
            else:
                chunks.extend(self._split(part, rest))
        if buffer:
            chunks.append(buffer)

        return [c.strip() for c in chunks if c.strip()]


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    cosine_similarity = dot(a, b) / (||a|| * ||b||)

    Returns 0.0 if either vector has zero magnitude.
    """
    if not vec_a or not vec_b:
        return 0.0

    norm_a = math.sqrt(_dot(vec_a, vec_a))
    norm_b = math.sqrt(_dot(vec_b, vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return _dot(vec_a, vec_b) / (norm_a * norm_b)


class ChunkingStrategyComparator:
    """Run all built-in chunking strategies and compare their results."""

    def compare(self, text: str, chunk_size: int = 200) -> dict:
        overlap = max(0, chunk_size // 10)
        strategies = {
            "fixed_size": FixedSizeChunker(chunk_size=chunk_size, overlap=overlap),
            "by_sentences": SentenceChunker(max_sentences_per_chunk=3),
            "recursive": RecursiveChunker(chunk_size=chunk_size),
        }

        comparison: dict = {}
        for name, chunker in strategies.items():
            chunks = chunker.chunk(text)
            total_length = sum(len(c) for c in chunks)
            comparison[name] = {
                "count": len(chunks),
                "avg_length": round(total_length / len(chunks), 2) if chunks else 0.0,
                "chunks": chunks,
            }
        return comparison


class HeadingChunker:
    """
    Chiến lược riêng cho Giai đoạn 2 — chia văn bản quy phạm theo ranh giới
    Điều / Chương / Phụ lục thay vì theo số ký tự.

    Cơ sở thiết kế (xem PHASE2_STRATEGY.md §1):
        Trong văn bản quy phạm, một "Điều" là một đơn vị ngữ nghĩa hoàn chỉnh và
        thường chứa trọn câu trả lời cho một câu hỏi. Cắt theo ký tự sẽ xé đôi
        quy định ở vị trí ngẫu nhiên; cắt theo Điều thì không.

    Hai điểm khác biệt so với 3 chiến lược có sẵn:
        1. Ranh giới chunk = ranh giới Điều/Chương/Phụ lục.
        2. Tiêu đề Điều được GHÉP VÀO nội dung mọi chunk con. Nhờ vậy đoạn
           "…đăng ký tối đa 24 TC…" của chương đại học phân biệt được với đoạn
           gần như giống hệt ở chương thạc sĩ (PHASE2_STRATEGY.md §5.4b).

    Quy tắc:
        - Điều ngắn hơn min_chunk_size được gộp với phần kế tiếp.
        - Điều dài hơn max_chunk_size được cắt tiếp bằng RecursiveChunker,
          mỗi mảnh con vẫn mang lại tiêu đề gốc.
        - Văn bản không có tiêu đề nào -> lùi về RecursiveChunker.
    """

    HEADING = re.compile(
        r"(?m)^[ \t]*(?:#{1,6}[ \t]*)?(?:\*\*)?[ \t]*"
        r"(?:Điều\s+\d+\s*[.:]|Chương\s+[IVXLC]+\b|Phụ\s+lục\s+[IVXLC0-9]+\b)"
    )
    HEADING_NOISE = re.compile(r"[#*]+")

    def __init__(
        self,
        min_chunk_size: int = 120,
        max_chunk_size: int = 900,
        separator: str = " — ",
    ) -> None:
        self.min_chunk_size = max(1, min_chunk_size)
        self.max_chunk_size = max(self.min_chunk_size, max_chunk_size)
        self.separator = separator

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []

        matches = list(self.HEADING.finditer(text))
        if not matches:
            return RecursiveChunker(chunk_size=self.max_chunk_size).chunk(text)

        pieces: list[str] = []

        # Phần mở đầu trước tiêu đề đầu tiên (căn cứ ban hành, mục lục...)
        preamble = text[: matches[0].start()].strip()
        if len(preamble) >= self.min_chunk_size:
            pieces.extend(RecursiveChunker(chunk_size=self.max_chunk_size).chunk(preamble))

        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            block = text[match.start() : end].strip()
            if not block:
                continue
            pieces.extend(self._split_section(block))

        return self._merge_short(pieces)

    def _split_section(self, block: str) -> list[str]:
        """Một section = 1 tiêu đề + thân. Cắt nhỏ nếu quá dài, luôn giữ tiêu đề."""
        heading_line, _, body = block.partition("\n")
        heading = self.HEADING_NOISE.sub("", heading_line).strip()
        body = body.strip()

        if not body:
            return [heading]
        if len(block) <= self.max_chunk_size:
            return [f"{heading}{self.separator}{body}"]

        budget = max(1, self.max_chunk_size - len(heading) - len(self.separator))
        return [
            f"{heading}{self.separator}{part}"
            for part in RecursiveChunker(chunk_size=budget).chunk(body)
        ]

    def _merge_short(self, pieces: list[str]) -> list[str]:
        """Gộp các mảnh ngắn hơn min_chunk_size vào mảnh kế tiếp."""
        chunks: list[str] = []
        buffer = ""
        for piece in pieces:
            buffer = piece if not buffer else f"{buffer}\n\n{piece}"
            if len(buffer) >= self.min_chunk_size:
                chunks.append(buffer)
                buffer = ""
        if buffer:
            if chunks:
                chunks[-1] = f"{chunks[-1]}\n\n{buffer}"
            else:
                chunks.append(buffer)
        return chunks
