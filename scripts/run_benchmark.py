"""Baseline + benchmark 5 câu hỏi của nhóm (B4 + B5).

    EMBEDDING_PROVIDER=local python3 scripts/run_benchmark.py

Chạy 4 chiến lược chunking trên cùng corpus `data/quydinh/`, cùng 5 câu hỏi
benchmark của nhóm (report/REPORT_NHOM.md), rồi ghi kết quả ra
`report/benchmark_results.md` — bảng Markdown dán thẳng vào báo cáo.

Cột "hit" là kiểm tra TỰ ĐỘNG: chunk có đúng doc_id kỳ vọng và có chứa từ khóa
của gold answer hay không. Nó chỉ là chỉ báo, KHÔNG thay thế việc đọc tay —
xem docs/SCORING.md (2/1/0 điểm mỗi câu).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ingest import chunk_document, load_documents  # noqa: E402
from src.src_thai_01801 import (  # noqa: E402
    ChunkingStrategyComparator,
    EmbeddingStore,
    FixedSizeChunker,
    HeadingChunker,
    KnowledgeBaseAgent,
    RecursiveChunker,
    SentenceChunker,
    _mock_embed,
)

DATA_DIR = Path(__file__).parent.parent / "data" / "quydinh"
OUT_PATH = Path(__file__).parent.parent / "report" / "benchmark_results.md"

STRATEGIES = {
    "fixed_size": FixedSizeChunker(chunk_size=900, overlap=90),
    "by_sentences": SentenceChunker(max_sentences_per_chunk=3),
    "recursive": RecursiveChunker(chunk_size=900),
    "heading": HeadingChunker(min_chunk_size=120, max_chunk_size=900),
}

# 5 câu hỏi nhóm chốt ở commit f254e9f + từ khóa kiểm chứng gold answer
QUERIES = [
    {
        "id": 1,
        "text": "Sinh viên không thuộc diện cảnh báo học tập được đăng ký tối đa và tối thiểu bao nhiêu tín chỉ trong một học kỳ chính?",
        "doc_id": "quy-che-dao-tao-2025",
        "keywords": ["24 TC", "12 TC"],
        "note": "bẫy: đoạn gần giống ở chương thạc sĩ cũng có 24/12 TC",
    },
    {
        "id": 2,
        "text": "Điều kiện để sinh viên được xét học bổng khuyến khích học tập loại A, B và C là gì?",
        "doc_id": "hoc-bong-kkht",
        "keywords": ["3,6", "3,2", "2,5"],
    },
    {
        "id": 3,
        "text": "Học phí chương trình đào tạo chuẩn năm học 2025-2026 được quy định như thế nào đối với các ngành Khoa học máy tính và Kỹ thuật hóa học?",
        "doc_id": "hoc-phi-2025-2026",
        "keywords": ["630", "550"],
        "note": "gold answer nằm trong BẢNG ở Phụ lục I",
    },
    {
        "id": 4,
        "text": "Chứng chỉ tiếng Anh dùng để xét miễn học các học phần ngoại ngữ cơ bản phải đáp ứng những điều kiện gì?",
        "doc_id": "quy-dinh-ngoai-ngu-k70",
        "keywords": ["kỹ năng", "năm"],
        "note": "gold answer trải trên Điều 3 VÀ Phụ lục II",
    },
    {
        "id": 5,
        "text": "Một học phần được coi là tương đương với học phần khác khi đáp ứng điều kiện nào về nội dung chuyên môn và số tín chỉ?",
        "doc_id": "quy-che-dao-tao-2025",
        "keywords": ["70%"],
    },
]

FILTER_QUERY = "Sinh viên nộp hồ sơ ở đâu và cần giấy tờ gì để được xác nhận kết quả học tập?"


def select_embedder():
    provider = os.getenv("EMBEDDING_PROVIDER", "mock").strip().lower()
    if provider == "local":
        from src.src_thai_01801 import LocalEmbedder

        return LocalEmbedder()
    return _mock_embed


def build_store(docs, chunker, embedder, name):
    chunk_docs = []
    for doc in docs:
        chunk_docs.extend(chunk_document(doc, chunker))
    store = EmbeddingStore(collection_name=f"bench_{name}", embedding_fn=embedder)
    store.add_documents(chunk_docs)
    return store, chunk_docs


def preview(text: str, width: int = 90) -> str:
    flat = " ".join(text.split())
    return (flat[:width] + "…") if len(flat) > width else flat


def main() -> int:
    embedder = select_embedder()
    backend = getattr(embedder, "_backend_name", "unknown")
    docs = load_documents(DATA_DIR)
    out: list[str] = []

    def emit(line: str = "") -> None:
        print(line)
        out.append(line)

    emit("# Kết quả Benchmark — Trương Văn Thái (E403-SpideyMen)")
    emit()
    emit(f"- Backend nhúng: `{backend}`")
    emit(f"- Corpus: {len(docs)} tài liệu trong `data/quydinh/`")
    emit(f"- Chiến lược cá nhân: **HeadingChunker** (chia theo Điều/Chương/Phụ lục)")
    emit()

    # ---------- B4: baseline ----------
    emit("## 1. Baseline — thống kê chunk theo chiến lược")
    emit()
    emit("| Chiến lược | Tổng chunk | Độ dài TB | Ngắn nhất | Dài nhất |")
    emit("|---|---:|---:|---:|---:|")

    stores = {}
    for name, chunker in STRATEGIES.items():
        store, chunk_docs = build_store(docs, chunker, embedder, name)
        stores[name] = store
        lengths = [len(c.content) for c in chunk_docs]
        emit(
            f"| `{name}` | {len(lengths)} | {sum(lengths) / len(lengths):.0f} "
            f"| {min(lengths)} | {max(lengths)} |"
        )
    emit()

    emit("### ChunkingStrategyComparator trên 2 tài liệu (theo yêu cầu Bài tập 3.1)")
    emit()
    emit("| Tài liệu | Chiến lược | count | avg_length |")
    emit("|---|---|---:|---:|")
    for doc in docs:
        if doc.id not in {"quy-che-dao-tao-2025", "hoc-bong-kkht"}:
            continue
        for strategy, stats in ChunkingStrategyComparator().compare(doc.content, chunk_size=900).items():
            emit(f"| {doc.id} | {strategy} | {stats['count']} | {stats['avg_length']} |")
        heading_chunks = STRATEGIES["heading"].chunk(doc.content)
        avg = sum(len(c) for c in heading_chunks) / max(1, len(heading_chunks))
        emit(f"| {doc.id} | **heading (của tôi)** | {len(heading_chunks)} | {avg:.2f} |")
    emit()

    # ---------- B5: benchmark ----------
    emit("## 2. Benchmark — 5 câu hỏi của nhóm, top-3 mỗi chiến lược")
    emit()
    scoreboard = {name: 0 for name in STRATEGIES}

    for query in QUERIES:
        emit(f"### Câu {query['id']}: {query['text']}")
        emit()
        if query.get("note"):
            emit(f"> Lưu ý: {query['note']}")
            emit()
        emit("| Chiến lược | # | Score | doc_id | Chunk (rút gọn) | Hit |")
        emit("|---|---:|---:|---|---|---|")
        for name, store in stores.items():
            results = store.search(query["text"], top_k=3)
            hit_rank = None
            for rank, result in enumerate(results, start=1):
                doc_ok = result["metadata"].get("doc_id") == query["doc_id"]
                kw_ok = any(k in result["content"] for k in query["keywords"])
                hit = doc_ok and kw_ok
                if hit and hit_rank is None:
                    hit_rank = rank
                emit(
                    f"| `{name}` | {rank} | {result['score']:.3f} "
                    f"| {result['metadata'].get('doc_id')} | {preview(result['content'])} "
                    f"| {'✅' if hit else ''} |"
                )
            if hit_rank == 1:
                scoreboard[name] += 2
            elif hit_rank:
                scoreboard[name] += 1
        emit()

    emit("### Bảng điểm tổng (tự động, theo docs/SCORING.md: top-1 đúng = 2đ, top-2/3 = 1đ)")
    emit()
    emit("| Chiến lược | Điểm /10 |")
    emit("|---|---:|")
    for name, score in sorted(scoreboard.items(), key=lambda kv: -kv[1]):
        emit(f"| `{name}` | {score} |")
    emit()

    # ---------- A/B metadata filter ----------
    emit("## 3. A/B metadata filter (chiến lược heading)")
    emit()
    emit(f"Câu hỏi: *{FILTER_QUERY}*")
    emit()
    store = stores["heading"]
    for label, results in [
        ("search() — không lọc", store.search(FILTER_QUERY, top_k=3)),
        (
            'search_with_filter(audience="student")',
            store.search_with_filter(FILTER_QUERY, top_k=3, metadata_filter={"audience": "student"}),
        ),
    ]:
        emit(f"**{label}**")
        emit()
        emit("| # | Score | doc_id | audience | Chunk (rút gọn) |")
        emit("|---:|---:|---|---|---|")
        for rank, result in enumerate(results, start=1):
            emit(
                f"| {rank} | {result['score']:.3f} | {result['metadata'].get('doc_id')} "
                f"| {result['metadata'].get('audience')} | {preview(result['content'], 70)} |"
            )
        emit()

    # ---------- Agent ----------
    emit("## 4. KnowledgeBaseAgent — kiểm tra grounding")
    emit()
    agent = KnowledgeBaseAgent(
        store=stores["heading"],
        llm_fn=lambda prompt: f"[prompt {len(prompt)} ký tự, {prompt.count('[')} chunk ngữ cảnh]",
    )
    emit(f"```\n{agent.answer(QUERIES[0]['text'], top_k=3)}\n```")
    emit()

    OUT_PATH.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"\n>>> Đã ghi {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
