# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Hà Hoàng Tuấn Hùng
**Nhóm:** Spideymen
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao (gần 1.0) nghĩa là hai đoạn văn bản có các vector embedding chỉ cùng hướng trong không gian ngữ nghĩa đa chiều. Điều này thể hiện rằng hai đoạn văn bản chia sẻ ý nghĩa hoặc chủ đề tương đồng, dù độ dài hay từ ngữ sử dụng có thể khác nhau.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Mèo là loài động vật bốn chân vô cùng đáng yêu."
- Câu B: "Những chú mèo bốn chân rất dễ thương."
- Tại sao tương đồng: Cả hai câu đều nói về cùng chủ thể (mèo) với thuộc tính (bốn chân) và tính chất tích cực (đáng yêu/dễ thương), khiến các vector hướng về cùng một phía trong không gian vector.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Thuật toán sắp xếp nhanh có độ phức tạp trung bình O(n log n)."
- Câu B: "Hôm nay trời nắng đẹp và không khí mát mẻ."
- Tại sao khác: Câu A thuộc chủ đề khoa học máy tính còn câu B thuộc chủ đề thời tiết. Hai câu hoàn toàn không liên quan về mặt ngữ nghĩa nên các vector tạo với nhau một góc lớn.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Độ tương tự cosine chỉ đo hướng góc của vector mà không bị ảnh hưởng bởi độ dài (magnitude). Trong khi đó, khoảng cách Euclid đo khoảng cách tuyệt đối giữa 2 điểm nên một đoạn văn ngắn và một đoạn văn dài có cùng nội dung vẫn sẽ bị tính là xa nhau.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* Công thức `số lượng chunk = ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.111...) = 23`
> *Đáp án:* 23 chunks

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Nếu overlap tăng lên 100, số lượng chunk tính được là `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = ceil(24.75) = 25` chunks (tăng thêm 2 chunks). Việc tăng độ chồng chéo giúp hạn chế hiện tượng mất ngữ cảnh tại đường ranh giới giữa hai chunks liền kề, giúp câu hoặc ý nghĩa bị ngắt đôi ở cuối chunk trước vẫn được lưu giữ trọn vẹn ở đầu chunk sau.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng regex `re.split(r'(?<=[.!?])\s+|\.\n', text)` kết hợp lookbehind để tách văn bản theo các ranh giới câu (`. `, `! `, `? `, `.\n`). Sau đó nhóm các câu đã được làm sạch khoảng trắng vào từng chunk với số lượng tối đa `max_sentences_per_chunk` câu và nối lại bằng khoảng trắng.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán duy trì danh sách ưu tiên dấu phân cách `["\n\n", "\n", ". ", " ", ""]`. Trường hợp cơ sở (base case) là khi chuỗi có độ dài `<= chunk_size`. Nếu vượt quá, thuật toán chọn dấu phân cách đầu tiên có trong chuỗi, tách thành các phần nhỏ, đệ quy chia nhỏ tiếp các phần còn quá lớn với danh sách dấu phân cách còn lại, rồi gộp các phần liên tiếp lại sao cho tổng độ dài mỗi chunk không vượt quá `chunk_size`.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Phương thức `add_documents` nhúng nội dung văn bản thông qua `_embedding_fn` và lưu record dưới dạng dictionary vào danh sách `self._store`. Phương thức `search` tạo vector embedding cho truy vấn, tính điểm tương đồng dot product (`_dot`) giữa truy vấn và từng chunk lưu trữ, sau đó sắp xếp giảm dần theo score và lấy top_k kết quả.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` thực hiện lọc thô trước (pre-filtering): duyệt danh sách `self._store` và chỉ giữ lại các chunk có `metadata` khớp chính xác với tất cả các cặp key-value trong `metadata_filter`, sau đó mới chạy `_search_records`. `delete_document` lọc bỏ tất cả bản ghi có `doc_id` trùng với metadata hoặc `id` bắt đầu bằng `doc_id::`, trả về True nếu có chunk bị xóa.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Phương thức `answer` gọi `self.store.search(question, top_k)` để truy xuất danh sách chunk liên quan nhất. Sau đó định dạng ngữ cảnh tìm được thành chuỗi và ghép vào prompt mẫu kèm câu hỏi, rồi truyền vào hàm `llm_fn` để sinh câu trả lời.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.11.0, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\AITHUCCHIEN\Labs\Day07-2A202601801-TruongVanThai
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

============================= 42 passed in 0.13s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | "Sinh viên phải đạt chuẩn đầu ra ngoại ngữ K70." | "Quy định điều kiện ngoại ngữ tốt nghiệp khóa K70." | cao | 0.892 | Đúng |
| 2 | "Mức thu học phí áp dụng cho năm học 2025-2026." | "Học phí năm học 2025-2026 tính theo định mức kinh tế kỹ thuật." | cao | 0.845 | Đúng |
| 3 | "Sinh viên nộp tiền đóng BHYT qua cổng thông tin ctt.hust.edu.vn." | "Hướng dẫn tham gia Bảo hiểm y tế bắt buộc." | cao | 0.768 | Đúng |
| 4 | "Quy trình thủ tục chuyển trường cho sinh viên." | "Điều kiện xét cấp học bổng khuyến khích học tập." | thấp | 0.124 | Đúng |
| 5 | "Giấy xác nhận sinh viên dùng để hoãn nghĩa vụ quân sự." | "Hôm nay trời nắng đẹp và gió nhẹ." | thấp | -0.042 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp số 3 ("nộp tiền đóng BHYT qua ctt.hust.edu.vn" vs "Hướng dẫn tham gia BHYT bắt buộc") có điểm thực tế cao (0.768) dù cách diễn đạt từ ngữ hoàn toàn khác nhau. Điều này cho thấy mô hình embedding biểu diễn được ngữ nghĩa tiềm ẩn (semantic meaning) và chủ đề thay vì chỉ khớp từ khóa (keyword matching).

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân trong gói `src` sử dụng chiến lược `RecursiveChunker(chunk_size=300)` kết hợp `search_with_filter`:

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Chuẩn đầu ra ngoại ngữ K70 | "Quy định chuẩn đầu ra ngoại ngữ từ khóa K70 hệ chính quy..." | 0.7929 | Có | Sinh viên K70 phải đạt chứng chỉ quốc tế hoặc bài thi chuẩn hóa đầu ra theo quy định của Trường. |
| 2 | Mức thu học phí 2025-2026 | "Tính bằng với mức học phí/một TCHP của chương trình đào tạo..." | 0.7547 | Có | Mức thu học phí được tính theo định mức kinh tế kỹ thuật ban hành cho năm học 2025-2026. |
| 3 | Điều kiện xét học bổng KKHT | "Quy định về việc xét cấp học bổng khuyến khích học tập..." | 0.8672 | Có | Sinh viên đạt kết quả học tập và rèn luyện từ Khá trở lên, không bị kỷ luật học kỳ xét thưởng. |
| 4 | Mức hỗ trợ ngân sách BHYT | "Mức thu và phương thức đóng BHYT - Được NSNN hỗ trợ tối thiểu 30%..." | 0.6887 | Có | Ngân sách nhà nước hỗ trợ tối thiểu 30% mức đóng, sinh viên chỉ đóng 70% còn lại. |
| 5 | Quy trình giấy xác nhận sinh viên | "Quy định công tác hành chính sinh viên - Đăng ký qua ctt.hust.edu.vn..." | 0.7168 | Có | Sinh viên đăng ký online qua ctt.hust.edu.vn, thời gian xử lý từ 1 đến 3 ngày làm việc. |


**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Việc kết hợp pre-filtering metadata trước khi thực hiện truy xuất tương đồng vector là yếu tố quyết định giúp loại bỏ thông tin nhiễu khi cơ sở dữ liệu chứa nhiều tài liệu thuộc các đơn vị quản lý khác nhau nhưng cùng dùng chung các thuật ngữ như "sinh viên", "quy định".

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


