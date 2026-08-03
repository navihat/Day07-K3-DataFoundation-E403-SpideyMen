# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Trương Thảo Nguyên
**Nhóm:** SpideyMen
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector embedding của hai đoạn văn bản chỉ "cùng hướng" (góc giữa chúng nhỏ, gần bằng 0), nghĩa là nội dung của chúng mang ý nghĩa ngữ nghĩa gần nhau — ví dụ cùng chủ đề, cùng từ vựng — dù độ dài văn bản có thể rất khác nhau.

**Ví dụ có độ tương tự CAO:**
- Câu A: Sinh viên cần mang thẻ sinh viên khi mượn sách ở thư viện.
- Câu B: Người dùng phải xuất trình thẻ thư viện hợp lệ để mượn tài liệu.
- Tại sao tương đồng: Cùng diễn đạt một quy trình (mượn tài liệu phải có thẻ), dùng chung từ khóa "thư viện/thẻ/mượn" và cùng vai nghĩa (điều kiện sử dụng dịch vụ mượn).

**Ví dụ có độ tương tự THẤP:**
- Câu A: Hạn nộp học phí là ngày 15 hàng tháng.
- Câu B: Thư viện mở cửa từ 7 giờ sáng.
- Tại sao khác: Hai chủ đề hoàn toàn khác nhau (tài chính/học vụ so với giờ phục vụ thư viện), hầu như không chia sẻ từ vựng, nên vector embedding nằm gần như vuông góc với nhau.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine chỉ xét GÓC giữa hai vector, bỏ qua độ lớn (magnitude), nên không bị ảnh hưởng bởi độ dài văn bản hay tần suất lặp từ — hai câu cùng ý nhưng khác độ dài vẫn đạt điểm cao. Khoảng cách Euclid lại bị thổi phồng bởi văn bản dài (vector có chuẩn lớn) dù nội dung có thể tương tự.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Phép tính: `số chunk = ceil((10,000 - 50) / (500 - 50)) = ceil(9,950 / 450) = ceil(22.111…) = 23`.
> Đáp án: **23 chunks**.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Với overlap=100: `ceil((10,000 - 100) / (500 - 100)) = ceil(9,900 / 400) = ceil(24.75) = 25 chunks` — tăng từ 23 lên 25 chunk. Overlap lớn hơn làm số chunk tăng (bước nhảy giảm) nhưng giúp giữ nguyên ngữ cảnh ở ranh giới cắt, giảm mất mát thông tin khi một câu/đoạn ý bị "cắt đôi" — cải thiện chất lượng truy xuất RAG.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng regex `(?<=[.!?])\s+` để tách theo ranh giới câu (dấu `.`, `!`, `?` theo sau bởi khoảng trắng/dấu xuống dòng), strip từng câu và lọc câu rỗng. Nhóm lần lượt tối đa `max_sentences_per_chunk` câu vào một chunk, nối bằng khoảng trắng; xử lý edge case text rỗng (trả về `[]`) và tham số bị hạ xuống tối thiểu 1.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán chia đệ quy kiểu LangChain: lần lượt thử các separator theo thứ tự ưu tiên (`\n\n`, `\n`, `. `, ` `, `""`). Base case: văn bản ≤ `chunk_size` → trả về nguyên chunk; hết separator → cắt cứng theo kích thước. Với mỗi separator, split rồi gộp các phần nhỏ lại cho tới khi vượt `chunk_size` (tránh chunk vô nghĩa quá ngắn), phần nào vẫn quá lớn thì đệ quy với các separator còn lại. Separator rỗng xử lý như cắt theo ký tự.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> `add_documents` nhúng từng `Document` qua `embedding_fn` và lưu record `{id, content, metadata, embedding}` (metadata được copy + bổ sung `doc_id`). `search` nhúng truy vấn rồi tính **tích vô hướng (dot product)** giữa vector truy vấn và mọi vector đã lưu, sort giảm dần và cắt lấy `top_k`; với ChromaDB thì dùng `collection.query(query_embeddings=[...])`.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` **lọc metadata TRƯỚC** (so khớp toàn bộ cặp key–value của `metadata_filter`), chỉ chạy similarity trên tập đã lọc; nếu không có filter thì delegate thẳng về `search` để hành vi nhất quán. `delete_document` xóa mọi record có `id == doc_id` hoặc `metadata['doc_id'] == doc_id` (hỗ trợ xóa cả bộ chunk sinh từ ingest), trả về `True` nếu có thay đổi.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Truy xuất `top_k` chunk từ store, nối nội dung thành khối NGỮ CẢNH, dựng prompt RAG gồm 3 phần (vai trò trợ lý + yêu cầu chỉ dựa vào ngữ cảnh, ngữ cảnh, câu hỏi) rồi truyền prompt vào `llm_fn`; kết quả LLM chính là câu trả lời — mô hình chuẩn retrieve → augment → generate.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts ==============================
platform darwin -- Python 3.11.15, pytest-9.1.1, pluggy-1.6.0
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================== 42 passed in 0.05s ==============================
```

**Số lượng bài test vượt qua (pass):** **42 / 42**

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

> Điểm thực tế tính bằng `compute_similarity(embed(a), embed(b))` với **mock embedder** (như README cảnh báo, mock sinh vector gần như ngẫu nhiên — chỉ phản ánh cơ chế tính toán, không phản ánh ngữ nghĩa tiếng Việt). Để có kết luận ngữ nghĩa thật cần `EMBEDDING_PROVIDER=local`.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên đăng ký môn học qua cổng học vụ. | Sinh viên đăng ký học phần trực tuyến. | cao | -0.064 | Không |
| 2 | Hạn nộp học phí là ngày 15 hàng tháng. | Thư viện mở cửa từ 7 giờ sáng. | thấp | -0.220 | Có |
| 3 | Sinh viên cần mang thẻ sinh viên khi mượn sách. | Người dùng phải xuất trình thẻ thư viện để mượn tài liệu. | cao | -0.084 | Không |
| 4 | Học bổng khuyến khích học tập dành cho sinh viên có GPA cao. | Sinh viên giỏi có thể nhận học bổng. | cao | 0.063 | Có |
| 5 | Ký túc xá nằm cạnh khu giảng đường. | Máy tính dùng thuật toán học máy để dự đoán dữ liệu. | thấp | -0.058 | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Bất ngờ nhất là cặp 1 và cặp 3 — hai cặp rõ ràng đồng nghĩa theo cảm nhận người đọc lại cho điểm âm/ngẫu nhiên. Điều này phản ánh đúng giới hạn của **mock embedder**: nó băm (hash) toàn bộ chuỗi nên "độ tương tự" gần như ngẫu nhiên, không học được ngữ nghĩa. Quan sát này nhắc lại bài học chính của lab: chỉ kết luận chất lượng retrieval/ngữ nghĩa khi dùng embedder thật (multilingual local hoặc OpenAI); mock chỉ để kiểm chứng cơ chế (tính toán, sắp xếp, pipeline).

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

> Chạy **5 câu hỏi đánh giá chung của nhóm** (xem `REPORT_NHOM.md` Phần 3) trên mã nguồn cá nhân của tôi trong gói `src`, dùng **chiến lược `FixedSizeChunker(500, 50)`** (chiến lược tôi được phân công trong nhóm), embedder đa ngữ local và bộ tài liệu nhóm đã hoàn thiện (`src/data/quydinh`). Kết quả benchmark đầy đủ nằm trong `src/data/quydinh/eval_results.json`.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời chuẩn của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Chuẩn đầu ra ngoại ngữ tiếng Anh đối với SV chính quy khóa K70 được quy định như thế nào? | `quy-dinh-ngoai-ngu-k70` — đầu tài liệu quy định chuẩn đầu ra ngoại ngữ K70 | 0.8121 | Có | SV K70 phải đạt chứng chỉ ngoại ngữ quốc tế (TOEIC, IELTS…) hoặc bài thi chuẩn hóa đầu ra theo quy định của Trường |
| 2 | Mức thu học phí năm học 2025–2026 áp dụng cho sinh viên như thế nào? | `quy-dinh-hoc-phi-2025-2026` — phần mức thu học phí 2025–2026 | 0.8016 | Có | Học phí áp dụng theo định mức kinh tế kỹ thuật ban hành cho từng nhóm ngành & CTĐT năm học 2025–2026 |
| 3 | Điều kiện về kết quả học tập & rèn luyện để sinh viên được xét cấp HB KKHT là gì? | `hoc-bong-khuyen-khich-hoc-tap` — Điều 2 các quy định chung | 0.8542 | Có | SV phải có kết quả học tập tích lũy & rèn luyện từ loại Khá trở lên, không bị kỷ luật trong học kỳ xét thưởng |
| 4 | Sinh viên tham gia BHYT bắt buộc được Ngân sách Nhà nước hỗ trợ bao nhiêu % mức đóng? | `huong-dan-bao-hiem-y-te` — Đối tượng & nghĩa vụ tham gia | 0.7354 | Có | NS nhà nước hỗ trợ tối thiểu 30% mức đóng BHYT, SV tự đóng 70% còn lại |
| 5 | Quy trình xin giấy xác nhận SV & thời gian giải quyết dịch vụ hành chính CTSV như thế nào? | `quy-dinh-hanh-chinh-sinh-vien` — phần cấp lại thẻ SV / đăng ký trực tuyến CTSV | 0.5582 | Có | Đăng ký trực tuyến qua ctt.hust.edu.vn (hoãn NVQS, vay vốn…), xử lý trong 1–3 ngày làm việc |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-1?** **5 / 5** — toàn bộ 5 câu đều có chunk liên quan ở vị trí top-1 với score cao (0.56–0.85). Với `FixedSizeChunker(500,50)`, tài liệu truy xuất cho từng câu khớp đúng với nguồn kiểm chứng của nhóm, khẳng định Pipeline đã hoạt động đúng trên corpus thật.

> **So sánh 3 chiến lược (từ `eval_results.json`):** cả 3 chiến lược đều cho top-1 đúng nguồn tài liệu cho 5 câu. `FixedSize(500,50)` cho score cao & ổn định nhất (q5 ở mức thấp nhất 0.558 nhưng vẫn đúng tài liệu CTSV). `SentenceChunker(3)` tạo snippet tách câu ngắn dễ đứt đoạn ngữ cảnh; `RecursiveChunker(300)` ở câu 5 trả về nhầm tài liệu BHYT thay vì nguồn hành chính CTSV. Nhận xét này là cơ sở để nhóm chọn chiến lược tốt nhất ở `REPORT_NHOM.md` Phần 2.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Với tài liệu quy định hành chính, **chunk giữ nguyên ranh giới điều chương (bằng Recursive split theo heading/newline)** truy xuất chính xác hơn rõ rệt so với chunk cắt theo số ký tự cố định. Ngoài ra, `metadata_filter` theo `audience` (student/faculty) giúp loại bỏ nhiễu giữa các nhóm đối tượng; với câu hỏi chỉ liên quan quy định dành riêng cho sinh viên, filter metadata ngay trong bước truy xuất cải thiện đáng kể chất lượng top-k.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
