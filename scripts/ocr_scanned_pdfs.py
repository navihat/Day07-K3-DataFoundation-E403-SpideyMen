"""OCR các PDF bản scan trong data/quydinh/ (B0a của PHASE2_STRATEGY.md).

Ba file dưới đây không có text layer nên `pymupdf4llm` đọc ra chuỗi rỗng.
Script render từng trang thành ảnh 300 DPI rồi cho EasyOCR (tiếng Việt) đọc.

    python3 scripts/ocr_scanned_pdfs.py            # OCR cả 3 file
    python3 scripts/ocr_scanned_pdfs.py QD_Hanh_chinh.pdf

Kết quả ghi ra `<slug>.ocr.txt` — **bản nháp cần sửa tay**, chưa phải tài liệu
nộp được. OCR tiếng Việt hay nhầm dấu thanh và số; mà số sai (mức tiền, số
ngày, điểm GPA) sẽ kéo theo gold answer sai. Đọc lại đối chiếu PDF gốc trước
khi chuyển thành `.md` có front matter.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "quydinh"
DPI = 300

# tên file PDF -> slug dùng cho doc_id/tên file đầu ra
SCANNED_PDFS = {
    "QD_Hanh_chinh.pdf": "quy-dinh-hanh-chinh",
    "huong_dan_bhyt.pdf": "huong-dan-bhyt",
    "thu_tuc_chuyen_truong.pdf": "thu-tuc-chuyen-truong",
}


def ocr_pdf(reader, pdf_path: Path, out_path: Path) -> int:
    import pymupdf

    doc = pymupdf.open(pdf_path)
    blocks: list[str] = []
    for page_number, page in enumerate(doc, start=1):
        image = page.get_pixmap(dpi=DPI).tobytes("png")
        # paragraph=True gộp các box cùng dòng/đoạn lại cho dễ đọc
        lines = reader.readtext(image, detail=0, paragraph=True)
        blocks.append(f"<!-- trang {page_number}/{len(doc)} -->")
        blocks.extend(lines)
        blocks.append("")
    text = "\n".join(blocks)
    out_path.write_text(text, encoding="utf-8")
    return len(text)


def main() -> int:
    import easyocr

    targets = sys.argv[1:] or list(SCANNED_PDFS)
    print("Nạp mô hình EasyOCR tiếng Việt (lần đầu sẽ tải model)...")
    started = time.time()
    reader = easyocr.Reader(["vi"], gpu=False)
    print(f"Sẵn sàng sau {time.time() - started:.0f}s\n")

    for name in targets:
        pdf_path = DATA_DIR / name
        if not pdf_path.exists():
            print(f"BỎ QUA (không thấy file): {pdf_path}")
            continue
        slug = SCANNED_PDFS.get(name, pdf_path.stem)
        out_path = DATA_DIR / f"{slug}.ocr.txt"

        started = time.time()
        size = ocr_pdf(reader, pdf_path, out_path)
        print(f"{name} -> {out_path.name}: {size} ký tự ({time.time() - started:.0f}s)")

    print("\nXong. Đọc lại và sửa tay trước khi chuyển thành .md có front matter.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
