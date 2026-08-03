# Chiến Lược Giai Đoạn 2 — Truy Xuất Quy Định Đại Học (K3)

> Tài liệu làm việc cho branch `thai`. Không phải bài nộp — bài nộp là `report/REPORT_NHOM.md` + `report/REPORT_CANHAN.md`.
> Cập nhật: 2026-08-03

---

## 0. Các quyết định đã chốt

| Hạng mục | Quyết định | Ghi chú |
|---|---|---|
| Phạm vi | Làm trọn phần cá nhân: corpus → chunker → benchmark → REPORT_CANHAN §4-5 | REPORT_NHOM để nhóm thống nhất |
| Chiến lược chunking | **Heading-aware theo Điều/Chương** | K3_VARIANT yêu cầu ≥1 thành viên làm kiểu này |
| Backend nhúng | `EMBEDDING_PROVIDER=local` (MiniLM đa ngữ) | `sentence-transformers 5.6.0` + `torch 2.13.0+cpu` đã cài |
| Thư mục corpus | `data/quydinh/` (file `.md` nằm cạnh PDF gốc) | `load_documents()` chỉ đọc `.md`/`.txt` nên PDF không lọt vào pipeline |
| PDF gốc | Giữ nguyên trong `data/quydinh/` | ⚠️ Rủi ro rubric — xem §7 |
| Nguồn URL metadata | Mình tra cứu web → bạn duyệt lại | URL không chắc chắn sẽ được đánh dấu `# CẦN KIỂM TRA` |
| Branch | `thai` | Merge vào `main` khi nhóm thống nhất |
| 5 benchmark queries | ✅ **Đã có** — commit `f254e9f` trong `report/REPORT_NHOM.md` | Đối chiếu ở §5.1 |
| Tài liệu khác `audience` | Bổ sung 1 văn bản staff/faculty **thật** | Để câu hỏi dùng filter có ý nghĩa, không gán nhãn theo phán đoán |
| Nhịp thực thi | **Chờ nhóm chốt 5 câu hỏi rồi làm một lượt B0→B6** | Chưa convert PDF trong lượt này |
| Header báo cáo | Trương Văn Thái — nhóm E403-SpideyMen | Ngày nộp để trống |
| 3 PDF bản scan | **OCR tại chỗ** (tesseract + gói `vie`) | Giữ đúng bộ tài liệu nhóm đã thu thập — xem B0 |

### Trạng thái công cụ (đã kiểm chứng 2026-08-03)

- `sentence-transformers 5.6.0` + `torch 2.13.0+cpu` ✓ — model MiniLM đa ngữ đã tải về cache, **384 chiều**, lần chạy đầu mất 239s, các lần sau tức thì.
- Kiểm tra tín hiệu: `sim("Thời hạn nộp học phí", "Hạn nộp học phí của sinh viên") = 0.757` vs `sim(học phí, thư viện) = 0.633`. Khoảng cách chỉ 0.12 vì test chạy bằng **tiếng Việt không dấu** — corpus và benchmark queries phải dùng **tiếng Việt có dấu** để model tách tín hiệu tốt hơn.
- `pymupdf4llm` ✓ đã cài để convert PDF.

---

## 1. Luận điểm trung tâm

Corpus của nhóm không phải văn xuôi tự do — nó là **văn bản quy phạm hành chính**, cấu trúc `Chương → Điều → Khoản`. Đây là món quà cho retrieval, vì:

> **Một "Điều" ≈ một đơn vị ngữ nghĩa hoàn chỉnh ≈ đúng một câu trả lời cho benchmark query.**

Người hỏi "Sinh viên phải nộp học phí trong bao lâu?" thì câu trả lời nằm gọn trong *Điều 13. Thời hạn nộp học phí* — không rải rác nhiều đoạn. Cắt theo ký tự (`FixedSizeChunker`) sẽ xé quy định đó làm đôi ở vị trí ngẫu nhiên; cắt theo Điều thì không.

Từ luận điểm này suy ra 3 quyết định thiết kế, và đây chính là phần được chấm 15đ "Strategy Design":

1. **Ranh giới chunk = ranh giới Điều** → chunk coherence cao, gold answer không bị cắt.
2. **Prepend tiêu đề Điều vào nội dung chunk** → embedding có tín hiệu từ khóa của tiêu đề ("học phí", "học bổng") ngay cả khi thân Điều dùng từ ngữ pháp lý vòng vo. Đây là điểm ăn tiền nhất với embedder đa ngữ.
3. **Metadata theo văn bản, không theo chunk** → cho phép A/B `search()` vs `search_with_filter()` để chứng minh tiện ích metadata (mục 3 của `docs/EVALUATION.md`).

---

## 2. Corpus & Metadata Schema

### 2.1 Kiểm kê corpus — ⚠️ chỉ 4/7 tài liệu dùng được ngay

Quét text layer bằng PyMuPDF ngày 2026-08-03:

| PDF | Trang | Số ký tự | `^Điều N` | Trạng thái |
|---|---:|---:|---:|---|
| `QCDT_2025_5445_QD-DHBK.pdf` | 34 | 78.420 | 99 | ✅ text, cấu trúc Điều rất rõ |
| `06_ Quy định ngoại ngữ từ K70...pdf` | 20 | 29.769 | 9 | ✅ text |
| `QD HOC PHI - 2025-2026-final.pdf` | 7 | 11.913 | 2 | ✅ text |
| `Quy định về việc xét cấp HB KKHT.pdf` | 3 | 5.003 | 7 | ✅ text |
| `QD_Hanh_chinh.pdf` | 4 | **82** | 0 | ❌ **bản scan** — không có text |
| `huong_dan_bhyt.pdf` | 1 | **0** | 0 | ❌ **bản scan** |
| `thu_tuc_chuyen_truong.pdf` | 1 | **0** | 0 | ❌ **bản scan** |

**Hệ quả:** corpus khả dụng = **4 tài liệu < 5 tối thiểu** theo `docs/DATA_COLLECTION.md` §1. Bắt buộc phải xử lý trước khi làm bất cứ việc gì khác — xem B0 ở §4.

### 2.1b Kết quả OCR (B0a — đã chạy 2026-08-03)

`scripts/ocr_scanned_pdfs.py` (PyMuPDF 300 DPI + EasyOCR `vi`), output `*.ocr.txt`:

| File | Ký tự | Thời gian | Chất lượng | Danh tính thật (đọc được từ OCR) |
|---|---:|---:|---|---|
| `quy-dinh-hanh-chinh.ocr.txt` | 5.308 | 105s | 🟢 Tốt — sai lặt vặt (`Số:600 IQĐ`, `hust edu vn` mất dấu chấm) | **QĐ 600/QĐ-ĐHBK (2023)** — Hướng dẫn thủ tục hành chính xác nhận văn bằng, chứng chỉ, kết quả học tập |
| `thu-tuc-chuyen-truong.ocr.txt` | 2.167 | 30s | 🟡 Khá — lỗi dấu (`djch`, `tin chỉ`, `vien`) | Hướng dẫn chuyển trường **cho du học sinh & sinh viên quốc tế** |
| `huong-dan-bhyt.ocr.txt` | 4.017 | 35s | 🔴 **Kém** — `huaho dan sihh VieN`, `Đol vởi sinh vi,n khỏg mởi nhặp hoc` | Hướng dẫn BHYT 2025-2026 — là **poster/infographic** chữ trang trí nên OCR vỡ |

**Xử lý:** file 1 và 2 sửa tay được (đối chiếu PDF, ~15 phút). File BHYT chỉ 1 trang nhưng OCR hỏng nặng — **chép tay nhanh hơn sửa**. Số liệu đọc được (789.750đ cho 15 tháng, 52.650đ/tháng, 631.800đ cho 12 tháng) phải soi lại PDF gốc từng con số, vì OCR nhầm số là kiểu lỗi nguy hiểm nhất cho gold answer.

### 2.2 Metadata sau khi biết nội dung thật

| File `.md` | `category` | `audience` | Trạng thái |
|---|---|---|---|
| `quy-che-dao-tao-2025.md` | dao-tao | student | ✅ text sạch — QCDT 5445/QĐ-ĐHBK |
| `quy-dinh-ngoai-ngu-k70.md` | ngoai-ngu | student | ✅ text sạch |
| `hoc-phi-2025-2026.md` | hoc-phi | student | ✅ text sạch |
| `hoc-bong-kkht.md` | hoc-bong | student | ✅ text sạch |
| `quy-dinh-hanh-chinh.md` | hanh-chinh | **all** | 🟢 OCR tốt, sửa tay nhẹ |
| `thu-tuc-chuyen-truong.md` | hoc-vu | student *(+`scope: international`)* | 🟡 OCR khá, sửa tay |
| ~~`huong-dan-bhyt.md`~~ | ~~y-te~~ | — | ❌ **Loại khỏi corpus** — poster, OCR hỏng nặng, không câu benchmark nào dùng tới |
| *(bổ sung)* | *(vd. coi-thi)* | **staff / faculty** | 🔎 vẫn thiếu — xem §2.3 |

**Corpus đạt 6 tài liệu** (yêu cầu 5-10) ✓ — nhưng **vẫn không có tài liệu nào `audience` là staff/faculty**.

### 2.2b Phát hiện: `audience: all` làm lộ điểm yếu của filter

`quy-dinh-hanh-chinh` áp dụng cho **cả người học lẫn cán bộ và tổ chức bên ngoài** (Điều 3 liệt kê "Trưởng phòng Đào tạo... các cán bộ viên chức, sinh viên") → gán `audience: all` mới đúng nội dung.

Nhưng `search_with_filter()` so khớp **chính xác** (`record["metadata"].get(key) == value`), nên lọc `{"audience": "student"}` sẽ **loại luôn tài liệu `all`** — dù tài liệu đó có liên quan tới sinh viên. Đây đúng là "Recall Trade-off" mà `docs/EVALUATION.md` §3 hỏi tới, và là một kết luận định lượng được, đáng viết vào báo cáo: *lọc metadata bằng so khớp chính xác trên trường phân cấp (`student` ⊂ `all`) sẽ mất recall; muốn đúng phải cho phép tập giá trị `{student, all}`.*

`audience` **gán theo nội dung thật sau khi đọc được văn bản**, không suy từ tên file. Bảng này là dự kiến, phải xác minh ở B1.

### 2.3 Tài liệu `audience` khác — bắt buộc bổ sung

K3_VARIANT yêu cầu ≥1 benchmark query cần `metadata_filter={"audience": "student"}`. Filter đó chỉ chứng minh được điều gì nếu corpus **có tài liệu không dành cho sinh viên** để bị loại ra. Cần tìm 1 văn bản công khai dành cho cán bộ/giảng viên — ví dụ quy định coi thi/chấm thi, quy trình thanh toán giờ giảng, quy định nhiệm vụ giảng viên. Tài liệu này vừa lấp chỗ trống corpus (4 → 5), vừa làm câu hỏi filter có ý nghĩa.

### 2.2 Front matter chuẩn (đủ 6 trường bắt buộc của K3)

```yaml
---
doc_id: hoc-phi-2025-2026
title: Quyết định về mức thu học phí năm học 2025-2026
source_url: https://...                 # CẦN KIỂM TRA
retrieved_at: 2026-08-03
document_version: "2025-2026"           # hoặc số/ngày quyết định
audience: student                       # student | faculty | staff | all
category: hoc-phi                       # trường lọc thứ 2 (bắt buộc ≥1)
department: phong-tai-chinh
language: vi
doc_type: quyet-dinh                    # quyet-dinh | quy-che | huong-dan
---
```

Kèm `data/quydinh/sources.csv` khớp 1-1, đúng header của `docs/DATA_COLLECTION.md` §5.

---

## 3. `HeadingChunker` — thiết kế

Thêm class mới vào `src/chunking.py`. **Không sửa** 4 class cũ để 42 test của Giai đoạn 1 giữ nguyên trạng thái pass.

### Thuật toán

```
1. Tách văn bản tại mọi vị trí khớp ^(Điều \d+\.|Chương [IVX]+|##+ )
2. Mỗi mảnh = (heading, body)
3. Chuẩn hoá: chunk_text = f"{heading} — {body}"      ← prepend tiêu đề
4. Điều quá NGẮN (< min_chunk_size)  → gộp với Điều kế tiếp
   (tránh chunk rác kiểu "Điều 4. Giải thích từ ngữ" chỉ 1 dòng)
5. Điều quá DÀI  (> max_chunk_size)  → cắt tiếp bằng RecursiveChunker,
   nhưng MỌI mảnh con đều được prepend lại heading gốc
   (giữ ngữ cảnh "mảnh này thuộc Điều nào")
6. Không khớp heading nào → fallback về RecursiveChunker (văn bản không cấu trúc)
```

### Khung code

```python
class HeadingChunker:
    """Chia văn bản quy phạm theo ranh giới Điều/Chương, giữ tiêu đề trong chunk."""

    HEADING = re.compile(
        r"^\s*(Điều\s+\d+[.:]|Chương\s+[IVXLC]+[.:]?|Phụ\s+lục\s+[IVXLC0-9]+|#{1,4}\s+)",
        re.MULTILINE,
    )   # "Phụ lục" bắt buộc phải có — câu benchmark 3 và 4 nằm trong phụ lục (§5.1c)

    def __init__(self, min_chunk_size=120, max_chunk_size=900): ...
    def chunk(self, text: str) -> list[str]: ...
```

### Vì sao thiết kế này thắng baseline (luận điểm cho báo cáo)

| Tiêu chí | `fixed_size` | `by_sentences` | `recursive` | `HeadingChunker` |
|---|---|---|---|---|
| Giữ trọn 1 quy định | ✗ cắt giữa Điều | ✗ vắt qua 2 Điều | ~ tuỳ chunk_size | ✓ theo thiết kế |
| Chunk biết mình thuộc Điều nào | ✗ | ✗ | ✗ | ✓ prepend heading |
| Xử lý "khoản 1., 2., 3." | ~ | ✗ tách sai vì nhiều dấu chấm | ~ | ✓ nằm trong Điều cha |
| Độ dài chunk đồng đều | ✓ | ~ | ✓ | ~ (Điều dài ngắn khác nhau) |

Điểm yếu phải thừa nhận trong báo cáo: độ dài chunk **không đồng đều** (Điều 2 dòng vs Điều 2 trang), và chunker **phụ thuộc chất lượng convert PDF** — nếu `pymupdf4llm` làm vỡ dòng "Điều 12." thì regex trượt. Đây là nguyên liệu tốt cho phần Failure Analysis (Bài tập 3.5).

---

## 4. Pipeline thực thi — 6 bước

- [ ] **B0. Vá lỗ hổng corpus (chặn mọi bước sau)** — mục tiêu: **≥5 tài liệu `.md` đọc được, trong đó ≥1 tài liệu không phải `audience: student`**.
  - **B0a. OCR 3 bản scan** (đã chọn): cài `tesseract-ocr` + gói ngôn ngữ `vie` (bản Windows: UB Mannheim installer, ~100MB, cài ngoài pip), rồi `pip install pytesseract` và render trang PDF → ảnh bằng PyMuPDF ở 300 DPI trước khi OCR. **Bắt buộc đọc lại và sửa tay** — OCR tiếng Việt có dấu hay nhầm dấu thanh, mà số liệu sai (mức tiền, số ngày) sẽ làm gold answer sai theo. Ưu tiên `QD_Hanh_chinh` (4 trang) vì nó có thể là tài liệu `audience` khác đang thiếu.
  - **B0b. Bổ sung tài liệu staff/faculty** nếu sau OCR vẫn không có văn bản nào ngoài `student` (§2.3).
- [x] **B1. Convert** ✅ 4 PDF → `.raw.md` bằng `scripts/convert_pdfs.py`. Kết quả + kiểm chứng gold answer ở §5.4.
- [x] **B2. Metadata** ✅ `scripts/build_corpus.py` → 6 file `.md` có front matter + `sources.csv`. `source_url: not-stated` (đã chốt bỏ qua tra cứu URL).
  - **Bẫy gặp phải:** `ingest.load_documents()` dùng `rglob` nên nuốt luôn file trung gian `.raw.md`/`.ocr.txt` → corpus bị nhân đôi bằng bản không metadata. Đã chuyển bản trung gian sang `build/intermediate/` (ngoài `data/`).
- [x] **B3. `HeadingChunker`** ✅ implement trong `src/src_thai_01801/chunking.py` (package cá nhân theo quy ước nhóm), export ở `__init__.py`, 10 test riêng ở `tests/test_heading_chunker.py`. **52/52 test pass** (42 gốc + 10 mới).
- [ ] **B4. Baseline** — `ChunkingStrategyComparator().compare()` trên 2-3 văn bản → bảng count/avg_length; chạy thêm `HeadingChunker` để so cùng bảng.
- [ ] **B5. Benchmark** — khi có 5 câu hỏi: chạy 4 chiến lược × 5 câu, ghi top-3 (score + chunk + relevant?), thêm A/B `search()` vs `search_with_filter(audience=student)`.
- [ ] **B6. Báo cáo** — điền REPORT_CANHAN §4 (dự đoán similarity 5 cặp câu) + §5 (bảng kết quả top-3); đưa số liệu baseline cho nhóm điền REPORT_NHOM.

Script hỗ trợ sẽ viết: `scripts/convert_pdfs.py` (B1), `scripts/run_benchmark.py` (B4-B5, xuất bảng Markdown dán thẳng vào báo cáo).

---

## 5.1 Bộ câu hỏi đã chốt — đối chiếu với chiến lược

Nhóm đã chốt 5 câu (commit `f254e9f`). Ba hệ quả:

**a) Blocker OCR được gỡ.** Cả 5 gold answer chỉ trích từ **4 PDF có text layer**: QCDT (câu 1, 5), HB KKHT (câu 2), học phí (câu 3), ngoại ngữ (câu 4). Không câu nào cần tới 3 bản scan. Nghĩa là **B0a không còn chặn benchmark** — có thể chạy B1→B6 ngay, OCR lùi xuống việc làm sau để đủ 5 tài liệu theo yêu cầu corpus.

**b) ⚠️ Thiếu câu hỏi cần `audience` filter.** Cả 5 câu đều nhắm tới sinh viên và **không câu nào cần `metadata_filter={"audience": "student"}`** mới trả lời đúng. K3_VARIANT bắt buộc có ít nhất một câu như vậy → nhóm cần sửa, nếu không sẽ mất điểm ở mục này.

**c) Hai câu chạm `Phụ lục`, không phải `Điều`:**

| Câu | Vị trí gold answer | Thách thức cho `HeadingChunker` |
|---|---|---|
| 3 | Quyết định học phí — **Phụ lục I** (bảng mức thu theo ngành) | Phụ lục là **bảng**, không phải Điều. Convert PDF dễ làm vỡ bảng |
| 4 | Quy định ngoại ngữ — **Điều 3 VÀ Phụ lục II** | Câu trả lời **nằm ở 2 chỗ** → không chunk nào chứa trọn gold answer |

→ Cập nhật regex heading ở §3 để bắt cả `Phụ lục [IVX]+`. Câu 4 gần như chắc chắn là **failure case** cho mọi chiến lược chunking (không chunk đơn lẻ nào đủ thông tin) — đây là nguyên liệu sẵn cho Bài tập 3.5, nên ghi lại kỹ thay vì cố sửa.

## 5.4 Kiểm chứng corpus vs gold answers (B1 — đã chạy)

Convert 4 PDF text layer bằng `scripts/convert_pdfs.py`:

| File | Ký tự | `Điều` | `Phụ lục` | Dòng bảng |
|---|---:|---:|---:|---:|
| `quy-che-dao-tao-2025` | 78.816 | 50 | 0 | 88 |
| `quy-dinh-ngoai-ngu-k70` | 32.039 | 7 | 8 | 163 |
| `hoc-phi-2025-2026` | 12.398 | 2 | 2 | 51 |
| `hoc-bong-kkht` | 4.938 | 7 | 0 | 0 |

**Cả 5 gold answer đều tìm thấy trong corpus** ✓ (24/12 TC · GPA 3,6 + ĐRL 90 · KHMT 630 & KTHH 550 · 4 kỹ năng + 2 năm · 70%). Nhưng quá trình kiểm chứng lộ ra hai vấn đề retrieval quan trọng hơn cả kết quả:

### 5.4a Lệch từ vựng: văn bản viết `TC`, câu hỏi viết `tín chỉ`

Quy chế ghi *"được đăng ký tối đa **24 TC** và tối thiểu **12 TC** trong học kỳ chính"*. Toàn bộ tài liệu chỉ có **đúng 1 chỗ** viết đầy đủ "tín chỉ" kèm số. Câu benchmark 1 lại hỏi bằng cụm "bao nhiêu **tín chỉ**".

→ Đây là bài kiểm tra thật cho embedding: khớp `tín chỉ` ↔ `TC` là việc **grep không làm được** mà embedding đa ngữ *có thể* làm được. Dự đoán trước khi chạy: câu 1 sẽ có score thấp hơn các câu khác. Ghi lại dự đoán này để đối chiếu — đúng loại phân tích mà rubric muốn.

### 5.4b Bẫy trùng lặp: cùng con số cho hai đối tượng khác nhau

Quy chế bao trùm cả 3 bậc học, và có **hai câu gần như giống hệt nhau**:

| Vị trí | Nội dung |
|---|---|
| Điều 10 (chương **đại học**) | "Sinh viên không thuộc diện cảnh báo học tập… đăng ký **tối đa 24 TC và tối thiểu 12 TC** trong học kỳ chính" |
| Điều tương ứng (chương **thạc sĩ**) | "**Học viên** có thể đăng ký **tối thiểu 12 TC và tối đa 24 TC** trong một học kỳ chính" |

Câu 1 hỏi về **sinh viên**. Nếu retrieval trả về đoạn của **học viên cao học**, kết quả *trông đúng* (cùng con số 24/12) nhưng **sai đối tượng** — kiểu lỗi nguy hiểm nhất vì rất khó phát hiện khi chấm nhanh.

→ **Đây là bằng chứng thực nghiệm cho quyết định thiết kế ở §1**: chunk trần chỉ chứa "…đăng ký tối đa 24 TC…" thì hai đoạn gần như không phân biệt được. Chunk có **prepend tiêu đề** thành *"Điều 10. Đăng ký học tập chương trình đại học — …"* thì tín hiệu "chương trình đại học" tách nó khỏi chương thạc sĩ. Nếu benchmark cho thấy `HeadingChunker` thắng ở đúng câu 1 trong khi `fixed_size` trả nhầm đoạn thạc sĩ, đó là kết quả đắt giá nhất của cả bài lab — nhớ ghi vào REPORT_NHOM §2.

## 5.3 Câu hỏi thứ 6 đề xuất — mang ra nhóm

**Vấn đề:** K3_VARIANT yêu cầu ≥1 câu cần `metadata_filter={"audience": "student"}`. Cả 5 câu hiện tại không câu nào cần.

**Nguyên lý thiết kế:** filter chỉ chứng minh được giá trị nếu câu hỏi **trùng từ khóa với tài liệu thuộc `audience` khác**. Nếu câu hỏi chỉ khớp đúng một tài liệu sinh viên thì có lọc hay không kết quả vẫn thế — filter trở thành trang trí. Vậy câu thứ 6 phải nhắm vào **vùng từ vựng chồng lấn** giữa văn bản cho sinh viên và văn bản cho cán bộ (thường là: hồ sơ, phê duyệt, quy trình, thời hạn nộp, thẩm quyền).

**Bản nháp (đã chỉnh theo nội dung thật đọc được sau OCR):**

> **Câu 6:** Sinh viên nộp hồ sơ ở đâu và cần chuẩn bị giấy tờ gì để được xác nhận kết quả học tập?
>
> - **Gold answer:** *(điền từ QĐ 600/QĐ-ĐHBK — mục II.2 và mục III sau khi sửa tay bản OCR)*
> - **Vì sao cần filter:** cụm "hồ sơ / Phòng Đào tạo / xác nhận / giấy tờ" xuất hiện dày ở **cả ba** tài liệu — QĐ 600 (`audience: all`), hướng dẫn chuyển trường (`student`), và Quy chế đào tạo (`student`). Không lọc, top-3 dễ trộn lẫn thủ tục chuyển trường của du học sinh với thủ tục xác nhận văn bằng: đúng chủ đề "hồ sơ, Phòng Đào tạo" nhưng **sai việc cần làm**.
> - **Cảnh báo phải kiểm chứng trước khi chốt:** theo §2.2b, lọc `{"audience": "student"}` sẽ **loại chính QĐ 600** vì nó gán `all`. Chạy thử trước: nếu gold answer nằm trong QĐ 600 thì filter làm kết quả **tệ đi**, và câu 6 phải đổi hướng (hoặc lọc bằng `category: hanh-chinh`, hoặc chờ có tài liệu staff thật rồi hỏi câu khác).

**Cách chứng minh trong báo cáo** (đây mới là phần ăn điểm, không phải bản thân câu hỏi): chạy cùng câu 6 hai lần, `search()` và `search_with_filter(metadata_filter={"audience": "student"})`, rồi đặt hai bảng top-3 cạnh nhau. Nếu bảng không lọc có chunk `audience: staff` lọt vào mà bảng có lọc thì không, đó là bằng chứng định lượng cho mục "Metadata Utility" của `docs/EVALUATION.md`.

**Điều kiện cần:** corpus phải có ít nhất một tài liệu `audience` ≠ `student` (§2.3). Nếu sau OCR mà `QD_Hanh_chinh` hóa ra vẫn hướng tới sinh viên thì phải bổ sung một văn bản dành cho cán bộ/giảng viên, nếu không câu 6 sẽ không chứng minh được gì.

## 5.2 Ràng buộc khi soạn benchmark (tham chiếu)

Gửi nhóm 4 ràng buộc này trước khi chốt câu hỏi — làm sai là mất điểm ở chỗ khó sửa lại:

1. **Đúng 5 câu**, đa dạng — không phải 5 biến thể của cùng một câu.
2. **≥1 câu bắt buộc cần** `metadata_filter={"audience": "student"}` mới trả lời đúng. Câu này chỉ có tác dụng nếu corpus có tài liệu `audience` khác (xem `quy-dinh-hanh-chinh` ở §2.1).
3. **Gold answer phải trích được nguyên văn từ corpus** — không suy đoán quy định trường. Nếu corpus không chứa câu trả lời thì đổi câu hỏi hoặc bổ sung tài liệu.
4. Nên có **1 câu số liệu cụ thể** (mức tiền/số ngày/điểm số) và **1 câu điều kiện** (ai đủ điều kiện được X) — hai dạng này phân biệt chiến lược chunking rõ nhất.

Gợi ý dạng câu hỏi hợp corpus hiện có: thời hạn nộp học phí · điều kiện xét học bổng KKHT · chuẩn ngoại ngữ đầu ra K70 · thủ tục chuyển trường cần giấy tờ gì · quy trình nào áp dụng cho cán bộ chứ không phải sinh viên (câu dùng filter).

---

## 6. Đo lường — ghi số gì

| Metric | Cách lấy | Vào mục báo cáo |
|---|---|---|
| count / avg_length mỗi chiến lược | `ChunkingStrategyComparator().compare()` | NHOM §2 Baseline |
| Top-3 relevant? (0/1/2 điểm) | Chấm tay theo `docs/SCORING.md` | NHOM §3 + CANHAN §5 |
| Score gap (top-1 − top-3) | In từ `search()` | CANHAN §5 — đo khả năng phân biệt tín hiệu/nhiễu |
| Filter có cải thiện không | So top-3 của `search()` vs `search_with_filter()` cùng câu | NHOM §3 |
| 5 cặp câu dự đoán similarity | `compute_similarity()` + LocalEmbedder | CANHAN §4 |

---

## 7. Rủi ro đã biết

| Rủi ro | Mức | Xử lý |
|---|---|---|
| **PDF gốc nằm trong `data/`** — `docs/DATA_COLLECTION.md` §3 ghi rõ "Không đưa PDF/HTML thô vào `data/`" | Trung bình — có thể bị trừ trong 10đ Document Set Quality | Bạn đã chọn giữ. Nếu muốn an toàn: `git mv data/quydinh/*.pdf raw/` là xong, pipeline không đổi |
| ~~3 PDF là bản scan~~ | ✅ **Đã xử lý** — OCR xong, corpus lên 7 tài liệu | Còn việc sửa tay: 2 file nhẹ, BHYT chép tay |
| **OCR nhầm số liệu** (789.750đ / 52.650đ / 631.800đ trong BHYT) | 🔴 Cao — số sai kéo gold answer sai theo | Soi từng con số với PDF gốc; may là benchmark hiện tại không hỏi tới BHYT |
| **Filter khớp chính xác loại nhầm tài liệu `all`** (§2.2b) | 🟡 Ảnh hưởng câu 6 | Kiểm chứng bằng thực nghiệm trước khi chốt câu 6; ghi vào báo cáo như một phát hiện |
| **Không có câu hỏi nào cần `audience` filter** | 🔴 Vi phạm yêu cầu bắt buộc của K3_VARIANT | Nhóm cần sửa/thêm 1 câu; kèm 1 tài liệu staff/faculty (§2.3) |
| Câu 4 có gold answer nằm ở 2 vị trí (Điều 3 + Phụ lục II) | 🟡 Không chiến lược nào truy xuất trọn trong 1 chunk | Không cố sửa — ghi thành failure case cho Bài tập 3.5 |
| Câu 3 cần đọc **bảng** trong Phụ lục I | Trung bình — convert PDF hay làm vỡ bảng | Kiểm tra kỹ output `pymupdf4llm` cho file học phí ở B1 |
| Corpus dùng tiếng Việt không dấu ở query | Trung bình — model đa ngữ tách tín hiệu kém hẳn | Benchmark queries bắt buộc viết **có dấu** |
| Convert làm vỡ dòng "Điều N." | Trung bình | Regex nới lỏng + kiểm tra thủ công; ghi vào Failure Analysis |
| `source_url` không tra được | Trung bình | Đánh dấu `# CẦN KIỂM TRA`, bạn duyệt; tuyệt đối không bịa URL |
| Corpus 7 tài liệu (danh nghĩa) | Thấp — yêu cầu 5-10 | Đạt về số lượng, **không đạt về chất lượng** cho tới khi xong B0 |

---

## 8. Ánh xạ sang thang điểm

| Việc trong file này | Mục rubric | Điểm |
|---|---|---|
| §2 corpus + metadata schema + sources.csv | Document Set Quality (nhóm) | 10 |
| §1 luận điểm + §3 thiết kế + bảng so sánh | Strategy Design (nhóm) | 15 |
| §5 §6 benchmark + A/B filter | Retrieval Quality (nhóm) | 10 |
| §7 failure analysis | Demo & bài học (nhóm) | 5 |
| B5 → CANHAN §5 | Competition Results (cá nhân) | 10 |
| B6 → CANHAN §4 | Similarity Predictions (cá nhân) | 5 |
