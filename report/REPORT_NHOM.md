# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Spideymen
**Thành viên:** Trương Văn Thái, Hà Hoàng Tuấn Hùng, Trương Thảo Nguyên, Bùi Linh Đan
**Ngày:** 03/08/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, ngoại ngữ, BHYT, thủ tục hành chính, chuyển trường tại Đại học Bách khoa Hà Nội).

**Phạm vi cụ thể nhóm tập trung:**
> Tập trung vào toàn bộ các văn bản quy định hành chính, chính sách học phí, học bổng, chuẩn đầu ra ngoại ngữ K70 và quy trình giải quyết thủ tục cho sinh viên chính quy Đại học Bách khoa Hà Nội.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Quy định chuẩn đầu ra ngoại ngữ K70 | https://ctt.hust.edu.vn/quy-dinh-ngoai-ngu-k70 | 2026-08-03 / 2025-2026 | 28,891 | `department: dao-tao`, `category: ngoai-ngu` |
| 2 | Quy chế đào tạo đại học 5445 QĐ-ĐHBK | https://ctt.hust.edu.vn/quy-che-dao-tao-5445 | 2026-08-03 / 2025 | 78,094 | `department: dao-tao`, `category: quy-che-dao-tao` |
| 3 | Quy định mức thu học phí năm 2025-2026 | https://ctt.hust.edu.vn/quy-dinh-hoc-phi-2025-2026 | 2026-08-03 / 2025-2026 | 11,819 | `department: tai-chinh`, `category: hoc-phi` |
| 4 | Quy định về xét cấp học bổng KKHT | https://ctt.hust.edu.vn/hoc-bong-kkht | 2026-08-03 / 2025 | 4,899 | `department: ctsv`, `category: hoc-bong` |
| 5 | Hướng dẫn thực hiện BHYT sinh viên | https://ctt.hust.edu.vn/huong-dan-bhyt | 2026-08-03 / 2025-2026 | 1,705 | `department: ctsv`, `category: bao-hiem` |
| 6 | Quy định công tác hành chính sinh viên | https://ctt.hust.edu.vn/quy-dinh-hanh-chinh | 2026-08-03 / 2025 | 1,395 | `department: ctsv`, `category: hanh-chinh` |
| 7 | Quy trình thủ tục xin chuyển trường | https://ctt.hust.edu.vn/thu-tuc-chuyen-truong | 2026-08-03 / 2025 | 1,521 | `department: dao-tao`, `category: thu-tuc` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | `str` | `quy-dinh-ngoai-ngu-k70` | Định danh duy nhất để phục vụ việc xoá/truy vết câu trả lời |
| `department` | `str` | `dao-tao`, `tai-chinh`, `ctsv` | Lọc chính xác đơn vị quản lý chuyên môn, tránh nhiễu thông tin giữa các phòng ban |
| `category` | `str` | `hoc-phi`, `hoc-bong`, `ngoai-ngu` | Pre-filtering khoanh vùng đúng phạm vi chủ đề của câu hỏi trước khi search vector |
| `audience` | `str` | `student` | Phân loại đối tượng áp dụng quy định |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên toàn bộ tài liệu (128,324 ký tự):

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| Bộ quy định Bách khoa (7 files) | FixedSizeChunker (`fixed_size`) | 459 | 299.6 ký tự | Ngắt quãng ngẫu nhiên theo số ký tự, đôi khi xé lẻ câu |
| Bộ quy định Bách khoa (7 files) | SentenceChunker (`by_sentences`) | 344 | 369.6 ký tự | Giữ nguyên cấu trúc ranh giới câu, ngữ cảnh mạch lạc |
| Bộ quy định Bách khoa (7 files) | RecursiveChunker (`recursive`) | 489 | 260.5 ký tự | Linh hoạt theo cấu trúc mục (`\n\n`, `\n`), tối ưu nhất cho văn bản quy định |

### Chiến lược của từng thành viên

**Thành viên 1 — Hà Hoàng Tuấn Hùng**
- **Loại chiến lược:** RecursiveChunker (chunk_size=300)
- **Mô tả & lý do chọn cho chủ đề này:** Phù hợp nhất với các văn bản văn phong pháp lý / quy định đại học vì tài liệu có cấu trúc phân cấp (Điều, Mục, Khoản) tách biệt rõ ràng bằng `\n\n` và `\n`.
- **Code snippet:**
```python
chunker = RecursiveChunker(separators=["\n\n", "\n", ". ", " ", ""], chunk_size=300)
```

**Thành viên 2 — Trương Văn Thái**
- **Loại chiến lược:** SentenceChunker (max_sentences_per_chunk=3)
- **Mô tả & lý do chọn:** Nhóm văn bản thành các khối tối đa 3 câu hoàn chỉnh để bảo đảm tính mạch lạc về mặt ngữ nghĩa và không làm đứt đoạn điều khoản quy định.
- **Code snippet:**
```python
chunker = SentenceChunker(max_sentences_per_chunk=3)
```

**Thành viên 3 — Trương Thảo Nguyên**
- **Loại chiến lược:** FixedSizeChunker (chunk_size=500, overlap=50)
- **Mô tả & lý do chọn:** Sử dụng cửa sổ trượt độ dài cố định 500 ký tự với độ chồng chéo 50 ký tự giúp giữ nguyên độ dài chunk đồng đều cho việc nhúng vector.
- **Code snippet:**
```python
chunker = FixedSizeChunker(chunk_size=500, overlap=50)
```

**Thành viên 4 — Bùi Linh Đan**
- **Loại chiến lược:** RecursiveChunker (chunk_size=200)
- **Mô tả & lý do chọn:** Sử dụng chia nhỏ đệ quy kích thước ngắn 200 ký tự để cô đọng thông tin chi tiết của từng điều khoản quy định nhỏ.
- **Code snippet:**
```python
chunker = RecursiveChunker(separators=["\n\n", "\n", ". ", " ", ""], chunk_size=200)
```

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Hà Hoàng Tuấn Hùng | RecursiveChunker (chunk_size=300) | 9 / 10 | Bám sát cấu trúc mục/đoạn văn bản quy định, ngắt đoạn tự nhiên | Cần tinh chỉnh danh sách separators phù hợp |
| Trương Văn Thái | SentenceChunker (max_sentences=3) | 8 / 10 | Giữ trọn vẹn ngữ nghĩa từng câu hoàn chỉnh | Số lượng câu có thể làm kích thước chunk không đều |
| Trương Thảo Nguyên | FixedSizeChunker (500, overlap=50) | 7 / 10 | Đơn giản, kích thước chunk đồng nhất | Có thể cắt ngang giữa câu hoặc điều khoản quy định |
| Bùi Linh Đan | RecursiveChunker (chunk_size=200) | 8.5 / 10 | Tập trung thông tin ngắn gọn, truy xuất chính xác câu ngắn | Đôi khi tách một điều khoản dài thành nhiều chunk nhỏ |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> **RecursiveChunker (chunk_size=300)** là chiến lược tốt nhất cho bộ dữ liệu quy định đại học. Nguyên nhân vì các văn bản quy chế, thông tư luôn được trình bày theo cấu trúc điều khoản chia dòng/đoạn rõ ràng. `RecursiveChunker` ưu tiên ngắt theo đoạn `\n\n` và dòng `\n` giúp giữ trọn vẹn từng mục điều khoản nhỏ mà không cắt ngang giữa câu như `FixedSizeChunker`.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Chuẩn đầu ra ngoại ngữ tiếng Anh đối với sinh viên chính quy khóa K70 được quy định như thế nào? | Sinh viên khóa K70 phải đạt chứng chỉ ngoại ngữ quốc tế (TOEIC, IELTS...) hoặc bài thi chuẩn hóa đầu ra theo khung năng lực quy định của Trường. | `quy-dinh-ngoai-ngu-k70` |
| 2 | Mức thu học phí năm học 2025-2026 áp dụng cho sinh viên như thế nào? | Mức thu học phí áp dụng theo quy định định mức kinh tế kỹ thuật ban hành cho từng nhóm ngành và chương trình đào tạo năm học 2025-2026. | `quy-dinh-hoc-phi-2025-2026` |
| 3 | Điều kiện về kết quả học tập và rèn luyện để sinh viên được xét cấp học bổng khuyến khích học tập (KKHT) là gì? | Sinh viên phải có kết quả học tập tích lũy và kết quả rèn luyện đạt từ loại Khá trở lên, không bị kỷ luật trong học kỳ xét thưởng. | `hoc-bong-khuyen-khich-hoc-tap` |
| 4 | Sinh viên tham gia Bảo hiểm y tế bắt buộc được Ngân sách Nhà nước hỗ trợ bao nhiêu phần trăm mức đóng? | Sinh viên được ngân sách nhà nước hỗ trợ tối thiểu 30% mức đóng BHYT, sinh viên tự đóng 70% còn lại. | `huong-dan-bao-hiem-y-te` |
| 5 | Quy trình xin giấy xác nhận sinh viên và thời gian giải quyết dịch vụ hành chính CTSV như thế nào? | Sinh viên đăng ký trực tuyến qua ctt.hust.edu.vn cho các mục đích hoãn NVQS, vay vốn..., thời gian xử lý từ 1 đến 3 ngày làm việc. | `quy-dinh-hanh-chinh-sinh-vien` |

### Tổng hợp chất lượng truy xuất của nhóm

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Chuẩn đầu ra ngoại ngữ K70 | FixedSize / SentenceChunker | Có (Top-1 score=0.8121) | Truy xuất chính xác văn bản `quy-dinh-ngoai-ngu-k70` |
| 2 | Mức thu học phí 2025-2026 | RecursiveChunker + Metadata Filter (`category: hoc-phi`) | Có (Top-1 score=0.7547) | Pre-filtering giúp loại bỏ nhiễu từ các văn bản đào tạo khác |
| 3 | Điều kiện cấp HB KKHT | RecursiveChunker (300) | Có (Top-1 score=0.8672) | Điểm số tương đồng ngữ nghĩa cao nhất toàn bộ benchmark |
| 4 | Mức hỗ trợ ngân sách BHYT | FixedSizeChunker + Metadata Filter (`category: bao-hiem`) | Có (Top-1 score=0.7354) | Truy xuất chính xác mục 2 trong Hướng dẫn BHYT |
| 5 | Quy trình xin giấy xác nhận sinh viên | SentenceChunker + Metadata Filter (`department: ctsv`) | Có (Top-1 score=0.6531) | Lọc theo phòng CTSV cho kết quả giấy xác nhận chính xác |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Lọc bằng metadata (`search_with_filter`) giúp ích **rất lớn**, đặc biệt ở các câu hỏi 2, 4 và 5. Việc pre-filtering theo `category: hoc-phi` hoặc `department: ctsv` giúp thu hẹp phạm vi tìm kiếm trước khi tính toán tương đồng vector, loại bỏ hoàn toàn các chunk nhiễu chứa các từ khóa chung như "sinh viên", "quy định" từ các văn bản đào tạo khác.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
1. Tầm quan trọng của pre-filtering metadata đối với bộ cơ sở dữ liệu quy định có nhiều thuật ngữ dùng chung.
2. Sự vượt trội của `RecursiveChunker` khi làm việc với văn bản pháp lý / quy chế có cấu trúc phân cấp.
3. Sự khác biệt giữa MockEmbedder (test kỹ thuật) và Semantic Embedder thực tế khi đánh giá điểm tương đồng.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng một bộ tài liệu nhưng việc thay đổi phương pháp chia nhỏ và kích thước chunk (chunk_size) tạo ra sự khác biệt rõ rệt về độ mạch lạc của thông tin. Chunk quá nhỏ sẽ làm đứt đoạn ý nghĩa điều khoản, trong khi chunk quá lớn gây nhiễu và làm giảm điểm số tương đồng cosine.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ thiết kế thêm các trường metadata chi tiết hơn như `section_heading` (tiêu đề mục) và thử nghiệm phương pháp chunking theo cặp Hỏi-Đáp (QA Chunking) cho các văn bản quy định thủ tục hành chính.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |

