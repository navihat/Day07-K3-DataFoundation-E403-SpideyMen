# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [Tên nhóm]
**Thành viên:** [Họ tên từng thành viên]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:**
> *1 câu — ví dụ: thư viện + đăng ký môn học.*

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [ ] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [ ] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| | | | |
| | | | |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| | FixedSizeChunker (`fixed_size`) | | | |
| | SentenceChunker (`by_sentences`) | | | |
| | RecursiveChunker (`recursive`) | | | |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — [Tên]**
- **Loại chiến lược:** [FixedSize / Sentence / Recursive / custom]
- **Mô tả & lý do chọn cho chủ đề này:** *(2-3 câu)*
- **Code snippet (nếu custom):**
```python
# Dán mã nguồn (implementation) vào đây
```

**Thành viên 2 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

**Thành viên 3 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| | | | | |
| | | | | |
| | | | | |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Viết 2-3 câu — đây là phần được đánh giá cao nhất (khả năng suy nghĩ & giải thích):*

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Nguồn kiểm chứng | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|------------------|--------------------------|
| 1 | Sinh viên không thuộc diện cảnh báo học tập được đăng ký tối đa và tối thiểu bao nhiêu tín chỉ trong một học kỳ chính? | Được đăng ký tối đa 24 tín chỉ và tối thiểu 12 tín chỉ trong học kỳ chính. Riêng sinh viên trình độ năm cuối không áp dụng ngưỡng tối thiểu. | Quy chế đào tạo, Điều 10 khoản 2.a | `QCDT_2025_5445_QD-DHBK.pdf` — Điều 10 khoản 2.a |
| 2 | Điều kiện để sinh viên được xét học bổng khuyến khích học tập loại A, B và C là gì? | Loại C: GPA ≥ 2,5 và điểm rèn luyện ≥ 65. Loại B: GPA ≥ 3,2 và điểm rèn luyện ≥ 80. Loại A: GPA ≥ 3,6 và điểm rèn luyện ≥ 90. | Quy định xét HB KKHT, Điều 3 | `Quy định về việc xét cấp HB KKHT.pdf` — Điều 3 |
| 3 | Học phí chương trình đào tạo chuẩn năm học 2025–2026 được quy định như thế nào đối với các ngành Khoa học máy tính và Kỹ thuật hóa học? | Khoa học máy tính: 630.000 đồng/TCHP. Kỹ thuật hóa học: 550.000 đồng/TCHP. | Quyết định học phí 2025–2026, Phụ lục I | `QD HOC PHI - 2025-2026-final.pdf` — Phụ lục I |
| 4 | Chứng chỉ tiếng Anh dùng để xét miễn học các học phần ngoại ngữ cơ bản phải đáp ứng những điều kiện gì? | Chứng chỉ phải còn hạn tại thời điểm nộp đơn xét miễn; chứng chỉ quốc gia/quốc tế phải được thẩm định nguồn gốc và cập nhật mức điểm lên hệ thống trước khi nộp đơn. Ngoài ra, chứng chỉ được quy đổi tương đương phải đánh giá đủ 4 kỹ năng nghe, nói, đọc, viết và chứng chỉ tiếng Anh phải được cấp trong vòng 2 năm tính đến thời điểm xét. | Quy định ngoại ngữ K70+, Điều 3 và Phụ lục II | `06_ Quy định ngoại ngữ từ K70_chính quy_final.pdf` — Điều 3 và Phụ lục II |
| 5 | Một học phần được coi là tương đương với học phần khác khi đáp ứng điều kiện nào về nội dung chuyên môn và số tín chỉ? | Hai học phần được coi là tương đương khi nội dung chuyên môn trùng lặp tối thiểu 70%. Học phần tương đương được dùng thay thế phải có số tín chỉ tối thiểu bằng hoặc lớn hơn học phần yêu cầu trong CTĐT. | Quy chế đào tạo, Điều 4 khoản 5.a | `QCDT_2025_5445_QD-DHBK.pdf` — Điều 4 khoản 5.a |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> *Viết 2-3 câu:*

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> *Liệt kê 2-3 ý:*

**Bài học rút ra khi so sánh trong nhóm:**
> *Viết 2-3 câu — cùng tài liệu nhưng chiến lược khác nhau dẫn tới khác biệt gì?*

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | / 10 |
| Thiết kế chiến lược (Strategy Design) | / 15 |
| Chất lượng truy xuất (Retrieval Quality) | / 10 |
| Thuyết trình (Demo) | / 5 |
| **Tổng phần nhóm** | **/ 40** |
