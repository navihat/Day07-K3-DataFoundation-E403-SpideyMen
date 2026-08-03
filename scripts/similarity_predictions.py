"""Bài tập 3.3 — dự đoán độ tương tự cosine trên 5 cặp câu (REPORT_CANHAN §4).

    EMBEDDING_PROVIDER=local python3 scripts/similarity_predictions.py

Các dự đoán dưới đây được ghi TRƯỚC khi chạy. Hai cặp 3 và 4 không chọn ngẫu
nhiên — chúng kiểm chứng đúng hai giả thuyết nêu ở PHASE2_STRATEGY.md §5.4:

    cặp 3 -> §5.4b: hai đoạn chỉ khác đối tượng (sinh viên / học viên) có bị
             embedding coi là gần như giống hệt nhau không?
    cặp 4 -> §5.4a: model có bắc được cầu giữa "tín chỉ" và viết tắt "TC" không?
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.src_thai_01801 import _mock_embed, compute_similarity  # noqa: E402

OUT_PATH = Path(__file__).parent.parent / "report" / "similarity_results.md"

PAIRS = [
    {
        "a": "Sinh viên được đăng ký tối đa bao nhiêu tín chỉ trong một học kỳ?",
        "b": "Số tín chỉ tối đa mà sinh viên được phép đăng ký trong học kỳ chính",
        "predict": "cao",
        "why": "cùng ý, chỉ khác cách diễn đạt — phép thử cơ bản nhất",
    },
    {
        "a": "Thời hạn nộp học phí của sinh viên là khi nào?",
        "b": "Điều kiện xét cấp học bổng khuyến khích học tập loại A",
        "predict": "thấp",
        "why": "khác chủ đề hoàn toàn, dù cùng miền văn bản quy định đại học",
    },
    {
        "a": "Sinh viên được đăng ký tối đa 24 TC trong học kỳ chính.",
        "b": "Học viên được đăng ký tối đa 24 TC trong một học kỳ chính.",
        "predict": "cao",
        "why": "BẪY (§5.4b): chỉ khác đúng một từ chỉ đối tượng, nhưng khác nhau về pháp lý",
    },
    {
        "a": "Sinh viên đăng ký tối đa 24 tín chỉ trong học kỳ chính.",
        "b": "Sinh viên đăng ký tối đa 24 TC trong học kỳ chính.",
        "predict": "cao",
        "why": "§5.4a: cùng nghĩa, chỉ khác viết tắt — nếu điểm THẤP thì câu 1 sẽ khó truy xuất",
    },
    {
        "a": "Chuẩn ngoại ngữ đầu ra đối với sinh viên K70",
        "b": "Quy định về chứng chỉ tiếng Anh để xét miễn học phần ngoại ngữ",
        "predict": "cao",
        "why": "liên quan nhưng không đồng nghĩa — kỳ vọng thấp hơn cặp 1",
    },
]


def select_embedder():
    if os.getenv("EMBEDDING_PROVIDER", "mock").strip().lower() == "local":
        from src.src_thai_01801 import LocalEmbedder

        return LocalEmbedder()
    return _mock_embed


def main() -> int:
    embedder = select_embedder()
    backend = getattr(embedder, "_backend_name", "unknown")

    rows = [
        "# Dự đoán độ tương tự cosine — Trương Văn Thái",
        "",
        f"Backend: `{backend}`",
        "",
        "| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |",
        "|---|---|---|---|---:|---|",
    ]
    print(f"Backend: {backend}\n")

    scores = []
    for index, pair in enumerate(PAIRS, start=1):
        score = compute_similarity(embedder(pair["a"]), embedder(pair["b"]))
        scores.append(score)
        # ngưỡng 0.70 chọn theo quan sát: MiniLM đa ngữ hiếm khi xuống dưới 0.5
        # với hai câu cùng tiếng Việt, nên "thấp" ở đây là tương đối
        actual = "cao" if score >= 0.70 else "thấp"
        correct = "✅" if actual == pair["predict"] else "❌"
        rows.append(
            f"| {index} | {pair['a']} | {pair['b']} | {pair['predict']} "
            f"| **{score:.3f}** | {correct} |"
        )
        print(f"{index}. {score:.3f}  (dự đoán {pair['predict']}, thực tế {actual}) {correct}")
        print(f"   {pair['why']}")

    rows.extend(["", "**Lý do chọn từng cặp:**", ""])
    for index, pair in enumerate(PAIRS, start=1):
        rows.append(f"{index}. {pair['why']}")

    OUT_PATH.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"\n>>> Đã ghi {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
