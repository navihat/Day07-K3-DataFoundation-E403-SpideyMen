"""Gắn YAML front matter cho corpus + sinh sources.csv (B2).

    python3 scripts/build_corpus.py

Đọc `<slug>.raw.md` (từ convert_pdfs.py) và `<slug>.ocr.txt` (từ ocr_scanned_pdfs.py),
ghi ra `<slug>.md` đúng định dạng docs/DATA_COLLECTION.md §4 rồi sinh `sources.csv`.

`source_url` để `not-stated`: bộ PDF do nhóm thu thập, chưa xác minh được URL gốc.
docs/DATA_COLLECTION.md §4 cho phép `not-stated` khi nguồn không nêu — nhưng nhóm
nên điền URL thật trước khi nộp để ăn trọn điểm "nguồn minh bạch".
"""
from __future__ import annotations

from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "quydinh"
# Bản trung gian phải nằm NGOÀI data/: ingest.load_documents() rglob mọi .md/.txt,
# để chúng lại trong data/ là corpus bị nhân đôi bằng bản không có front matter.
INTERMEDIATE_DIR = Path(__file__).parent.parent / "build" / "intermediate"
RETRIEVED_AT = "2026-08-03"

# slug -> (file nguồn, metadata bổ sung)
CORPUS = {
    "quy-che-dao-tao-2025": {
        "source": "quy-che-dao-tao-2025.raw.md",
        "title": "Quy chế đào tạo của Đại học Bách khoa Hà Nội",
        "document_version": "5445/QĐ-ĐHBK (2025)",
        "audience": "student",
        "category": "dao-tao",
        "department": "phong-dao-tao",
        "doc_type": "quy-che",
    },
    "quy-dinh-ngoai-ngu-k70": {
        "source": "quy-dinh-ngoai-ngu-k70.raw.md",
        "title": "Quy định về chuẩn ngoại ngữ đối với sinh viên chính quy từ K70",
        "document_version": "not-stated",
        "audience": "student",
        "category": "ngoai-ngu",
        "department": "phong-dao-tao",
        "doc_type": "quy-dinh",
    },
    "hoc-phi-2025-2026": {
        "source": "hoc-phi-2025-2026.raw.md",
        "title": "Quyết định về mức thu học phí năm học 2025-2026",
        "document_version": "2025-2026",
        "audience": "student",
        "category": "hoc-phi",
        "department": "phong-ke-hoach-tai-chinh",
        "doc_type": "quyet-dinh",
    },
    "hoc-bong-kkht": {
        "source": "hoc-bong-kkht.raw.md",
        "title": "Quy định về việc xét cấp học bổng khuyến khích học tập",
        "document_version": "not-stated",
        "audience": "student",
        "category": "hoc-bong",
        "department": "phong-cong-tac-sinh-vien",
        "doc_type": "quy-dinh",
    },
    "quy-dinh-hanh-chinh": {
        "source": "quy-dinh-hanh-chinh.ocr.txt",
        "title": "Hướng dẫn thủ tục hành chính về xác nhận văn bằng, chứng chỉ, kết quả học tập",
        "document_version": "600/QĐ-ĐHBK (2023)",
        # Điều 3 nêu đối tượng thi hành gồm cả cán bộ viên chức lẫn sinh viên
        # -> "all" mới đúng nội dung. Xem PHASE2_STRATEGY.md §2.2b.
        "audience": "all",
        "category": "hanh-chinh",
        "department": "phong-dao-tao",
        "doc_type": "huong-dan",
        "extraction": "ocr-chua-soat",
    },
    "thu-tuc-chuyen-truong": {
        "source": "thu-tuc-chuyen-truong.ocr.txt",
        "title": "Hướng dẫn thủ tục chuyển trường cho du học sinh và sinh viên quốc tế",
        "document_version": "not-stated",
        "audience": "student",
        "category": "hoc-vu",
        "department": "phong-dao-tao",
        "doc_type": "huong-dan",
        "scope": "international",
        "extraction": "ocr-chua-soat",
    },
}

FIELD_ORDER = [
    "doc_id", "title", "source_url", "retrieved_at", "document_version",
    "audience", "category", "department", "language", "doc_type",
    "scope", "extraction",
]


def build_front_matter(slug: str, meta: dict) -> str:
    values = {
        "doc_id": slug,
        "source_url": "not-stated",
        "retrieved_at": RETRIEVED_AT,
        "language": "vi",
        **{k: v for k, v in meta.items() if k != "source"},
    }
    lines = ["---"]
    for field in FIELD_ORDER:
        if field not in values:
            continue
        value = values[field]
        # bọc nháy cho giá trị dễ bị YAML hiểu thành số/ngày
        needs_quote = field in {"document_version", "retrieved_at"} or ":" in str(value)
        lines.append(f'{field}: "{value}"' if needs_quote else f"{field}: {value}")
    lines.append("---")
    return "\n".join(lines)


def main() -> int:
    INTERMEDIATE_DIR.mkdir(parents=True, exist_ok=True)
    rows = ["doc_id,file_path,title,source_url,retrieved_at,document_version,license_or_permission"]
    print(f"{'file':<26} {'ký tự':>8}  audience")
    print("-" * 50)

    for slug, meta in CORPUS.items():
        src_path = DATA_DIR / meta["source"]
        if not src_path.exists():  # đã dọn sang build/intermediate/ ở lần chạy trước
            src_path = INTERMEDIATE_DIR / meta["source"]
        if not src_path.exists():
            print(f"BỎ QUA (không thấy): {meta['source']}")
            continue

        body = src_path.read_text(encoding="utf-8").strip()
        out_path = DATA_DIR / f"{slug}.md"
        out_path.write_text(f"{build_front_matter(slug, meta)}\n\n{body}\n", encoding="utf-8")

        title = meta["title"].replace(",", " ")  # tránh vỡ cột CSV
        rows.append(
            f'{slug},data/quydinh/{slug}.md,{title},not-stated,'
            f'{RETRIEVED_AT},{meta["document_version"]},team-collected'
        )
        print(f"{slug:<26} {len(body):>8}  {meta['audience']}")

        # dọn bản trung gian ra khỏi data/ để corpus chỉ còn file .md có metadata
        if src_path.parent == DATA_DIR:
            src_path.replace(INTERMEDIATE_DIR / src_path.name)

    (DATA_DIR / "sources.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"\nsources.csv: {len(rows) - 1} dòng")
    print("LƯU Ý: source_url đang là 'not-stated' — nhóm nên điền URL thật trước khi nộp.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
