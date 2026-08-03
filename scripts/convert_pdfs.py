"""Convert các PDF có text layer trong data/quydinh/ sang Markdown (B1).

    python3 scripts/convert_pdfs.py

Dùng `pymupdf4llm` để giữ tiêu đề, danh sách và bảng. Ghi ra `<slug>.raw.md`
— bản thô CHƯA có YAML front matter; bước B2 mới gắn metadata.

Ba file bản scan không nằm ở đây: xem `scripts/ocr_scanned_pdfs.py`.

Script in ra số mốc `Điều N` và `Phụ lục` giữ được sau khi convert — đây là chỉ
số quan trọng nhất, vì `HeadingChunker` cắt chunk dựa đúng vào các mốc đó.
"""
from __future__ import annotations

import re
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "quydinh"

# PDF có text layer -> slug (khớp doc_id dùng ở PHASE2_STRATEGY.md §2.2)
TEXT_PDFS = {
    "QCDT_2025_5445_QD-DHBK.pdf": "quy-che-dao-tao-2025",
    "QD HOC PHI - 2025-2026-final.pdf": "hoc-phi-2025-2026",
    "Quy định về việc xét cấp HB KKHT.pdf": "hoc-bong-kkht",
    "06_ Quy định ngoại ngữ từ K70_chính quy_final.pdf": "quy-dinh-ngoai-ngu-k70",
}

DIEU = re.compile(r"(?m)^\s*(?:#+\s*)?(?:\*\*)?Điều\s+\d+")
PHU_LUC = re.compile(r"(?m)^\s*(?:#+\s*)?(?:\*\*)?Phụ\s+lục", re.IGNORECASE)
TABLE_ROW = re.compile(r"(?m)^\s*\|.*\|\s*$")


def main() -> int:
    import pymupdf4llm

    print(f"{'file':<28} {'ký tự':>8} {'Điều':>6} {'Phụ lục':>8} {'dòng bảng':>10}")
    print("-" * 66)
    for name, slug in TEXT_PDFS.items():
        pdf_path = DATA_DIR / name
        if not pdf_path.exists():
            print(f"BỎ QUA (không thấy): {name}")
            continue

        markdown = pymupdf4llm.to_markdown(str(pdf_path), show_progress=False)
        out_path = DATA_DIR / f"{slug}.raw.md"
        out_path.write_text(markdown, encoding="utf-8")

        print(
            f"{slug:<28} {len(markdown):>8} {len(DIEU.findall(markdown)):>6} "
            f"{len(PHU_LUC.findall(markdown)):>8} {len(TABLE_ROW.findall(markdown)):>10}"
        )

    print("\nKiểm tra thủ công trước khi sang B2: mốc 'Điều N' còn nguyên dòng chứ?")
    print("Riêng hoc-phi-2025-2026: Phụ lục I là BẢNG mức thu — soi kỹ bảng có vỡ không.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
