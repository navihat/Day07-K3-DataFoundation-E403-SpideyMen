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
    def __init__(self, max_sentences_per_chunk: int = 3) -> None:
        self.max_sentences_per_chunk = max(1, max_sentences_per_chunk)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        # Tách theo ranh giới câu: ". ", "! ", "? ", ".\n", "!\\n", "?\\n"
        # (?<=[.!?])   : lookbehind — ký tự trước là ., ! hoặc ?
        # \\s+|\\n+    : theo sau là khoảng trắng hoặc newline
        parts = re.split(r"(?<=[.!?])\s+|(?<=[.!?])\n+", text)
        sentences = [p.strip() for p in parts if p and p.strip()]
        if not sentences:
            return []

        chunks: list[str] = []
        n = self.max_sentences_per_chunk
        for i in range(0, len(sentences), n):
            group = sentences[i : i + n]
            chunks.append(" ".join(group).strip())
        return chunks

class RecursiveChunker:
    DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]

    def __init__(self, separators: list[str] | None = None, chunk_size: int = 500) -> None:
        self.separators = self.DEFAULT_SEPARATORS if separators is None else list(separators)
        self.chunk_size = chunk_size

    def chunk(self, text: str) -> list[str]:
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]
        return self._split(text, list(self.separators))

    def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
        # Base case: không còn separator nào
        if not remaining_separators:
            return [current_text]

        # Base case: đã đủ nhỏ
        if len(current_text) <= self.chunk_size:
            return [current_text]

        separator = remaining_separators[0]
        rest = remaining_separators[1:]

        # Fallback cuối: cắt cứng theo chunk_size
        if separator == "":
            return [
                current_text[i : i + self.chunk_size]
                for i in range(0, len(current_text), self.chunk_size)
            ]

        pieces = current_text.split(separator)
        result: list[str] = []
        for piece in pieces:
            if len(piece) <= self.chunk_size:
                result.append(piece)
            else:
                # Đoạn vẫn quá lớn → đệ quy với separator nhỏ hơn
                result.extend(self._split(piece, rest))
        return result


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def compute_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    dot = _dot(vec_a, vec_b)
    norm_a = math.sqrt(_dot(vec_a, vec_a))
    norm_b = math.sqrt(_dot(vec_b, vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)

class ChunkingStrategyComparator:
    def compare(self, text: str, chunk_size: int = 200) -> dict:
        fixed = FixedSizeChunker(chunk_size=chunk_size, overlap=50)
        by_sentence = SentenceChunker(max_sentences_per_chunk=3)
        recursive = RecursiveChunker(chunk_size=chunk_size)

        strategies = {
            "fixed_size": fixed.chunk(text),
            "by_sentences": by_sentence.chunk(text),
            "recursive": recursive.chunk(text),
        }

        result: dict = {}
        for name, chunks in strategies.items():
            if chunks:
                avg = sum(len(c) for c in chunks) / len(chunks)
                result[name] = {
                    "count": len(chunks),
                    "avg_length": avg,
                    "chunks": chunks,
                }
            else:
                result[name] = {"count": 0, "avg_length": 0.0, "chunks": []}
        return result
