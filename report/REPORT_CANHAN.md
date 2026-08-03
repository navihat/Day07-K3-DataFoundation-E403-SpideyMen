# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Bùi Linh Đan
**Nhóm:** SpideyMen
**Ngày:** 2026-08-03

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector có góc giữa chúng nhỏ, nghĩa là hai văn bản cùng hướng trong không gian embedding → nội dung tương đồng về ngữ nghĩa. Giá trị trong khoảng [-1, 1]: 1 = giống hệt, 0 = không liên quan, -1 = đối lập.

**Ví dụ có độ tương tự CAO:**
- Câu A: Sinh viên đăng ký học phần trên cổng học vụ
- Câu B: SV đăng ký môn học qua cổng online của trường
- Tại sao tương đồng: Cùng chủ đề (đăng ký môn học), cùng đối tượng (sinh viên), cùng ngữ cảnh (cổng trường)

**Ví dụ có độ tương tự THẤP:**
- Câu A: Học phí được đóng theo học kỳ
- Câu B: Thư viện mở cửa 24/7
- Tại sao khác: Chủ đề hoàn toàn khác nhau (tài chính vs cơ sở vật chất)

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine chỉ đo góc giữa hai vector (hướng ngữ nghĩa), không phụ thuộc độ dài văn bản. Văn bản dài/ngắn có thể cùng chủ đề nhưng magnitude khác nhau — Euclidean bị ảnh hưởng bởi magnitude nên đánh giá sai. Với text embedding (đã chuẩn hóa L2 hoặc dùng cosine), chỉ hướng mới mang ý nghĩa.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Áp dụng công thức: `số chunk = ceil((độ_dài - overlap) / (chunk_size - overlap))`
> `= ceil((10000 - 50) / (500 - 50))`
> `= ceil(9950 / 450)`
> `= ceil(22.11)`
> `= 23 chunks`
> Đáp án: **23 chunks**

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Với overlap=100: `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = ceil(24.75) = 25 chunks` — tăng từ 23 lên 25 chunks (~9%).
> Tăng overlap vì: (1) giữ liên kết ngữ cảnh giữa 2 chunk liền kề (nếu chunk A kết thúc giữa một quy trình nhiều bước, chunk B vẫn chứa phần đầu giúp LLM hiểu trọn vẹn); (2) giảm rủi ro mất thông tin quan trọng ở ranh giới chunk. Đánh đổi: tăng overlap → tăng số chunk → tăng chi phí lưu trữ và retrieval. Thường chọn overlap = 10-20% chunk_size.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng regex `(?<=[.!?])\s+|(?<=[.!?])\n+` (lookbehind giữ lại dấu `.!?` phía trước) để tách câu, vì regex lookbehind đảm bảo dấu kết thúc câu nằm trong đoạn vừa tách (không bị mất khi ghép lại). Sau đó gom nhóm `max_sentences_per_chunk` câu liên tiếp thành 1 chunk, nối bằng dấu cách. Edge case: text rỗng hoặc chỉ chứa khoảng trắng → trả `[]`; nếu regex không tách được câu nào → cũng trả `[]`. Hàm `__init__` đảm bảo `max_sentences_per_chunk >= 1` bằng `max(1, ...)`.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> `chunk` là entry point: nếu text ngắn hơn `chunk_size` → trả luôn `[text]`, nếu không → gọi `_split(text, separators)`. `_split` thử separator đầu tiên trong danh sách (ưu tiên `\n\n` → `\n` → `. ` → ` ` → `""`); với mỗi đoạn sau split, nếu đoạn vẫn > chunk_size thì đệ quy với separator nhỏ hơn. Base case: hết separator hoặc đoạn đã đủ nhỏ. Khi separator = `""` (fallback cuối) → cắt cứng theo `chunk_size`. Ưu điểm: ưu tiên ranh giới ngữ nghĩa tự nhiên (đoạn văn, dòng, câu) trước khi cắt nhỏ.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> `add_documents` duyệt từng `Document`, gọi `_make_record` để tạo dict `{id, content, embedding, metadata}` (embedding sinh từ `self._embedding_fn(content)`), append vào `self._store`. `search` embed query rồi gọi `_search_records(query, self._store, top_k)`. `_search_records` tính dot product giữa query vector và embedding từng record — vì `_mock_embed` đã chuẩn hóa L2 nên dot = cosine similarity; sort desc theo score, lấy top_k. Trong `__init__` có thử `import chromadb`; nếu có sẵn thì set `_use_chroma=True`, nhưng toàn bộ test dùng in-memory.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` lọc **trước** khi search: nếu `metadata_filter` rỗng/None → gọi `search()` bình thường; nếu không, giữ lại record có `metadata` chứa **tất cả** key=value trong filter (dùng `all()`), rồi mới chạy `_search_records` trên tập con. `delete_document` đếm size trước, lọc bỏ record có `metadata['doc_id']` (fallback `record['id']` khi metadata rỗng) khớp `doc_id`, trả `True` nếu size giảm, `False` nếu không tìm thấy. Fallback `record['id']` giúp xử lý các test case mà document được thêm vào không kèm metadata.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> `answer` thực hiện 3 bước: (1) `self.store.search(question, top_k)` lấy top-k chunk liên quan; (2) format prompt theo cấu trúc "Bạn là trợ lý trả lời dựa trên ngữ cảnh được cung cấp → Ngữ cảnh → Câu hỏi → Câu trả lời:" với context là danh sách chunk đánh số `[Đoạn 1]... [Đoạn 2]...` nối bằng 2 newline; (3) gọi `self.llm_fn(prompt)` trả về câu trả lời. Nếu store rỗng/không có chunk nào → trả thông báo "Không tìm thấy thông tin liên quan..." thay vì gọi LLM. `__init__` chỉ lưu reference `self.store` và `self.llm_fn` để dùng sau.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.11.8, pytest-9.1.1, pluggy-1.6.0 -- F:\VinAI\Day07-K3-DataFoundation-E403-SpideyMen\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: F:\VinAI\Day07-K3-DataFoundation-E403-SpideyMen
plugins: anyio-4.14.2
collecting ... collected 42 items

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

============================= 42 passed in 0.17s ==============================

```

**Số lượng bài test vượt qua (pass):** 42/42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Chạy `compute_similarity(_mock_embed(a), _mock_embed(b))` trên 5 cặp câu tiếng Việt đa dạng chủ đề. Dự đoán **trước** dựa trên mức độ cùng chủ đề của 2 câu.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên đăng ký học phần trên cổng học vụ | SV đăng ký môn học qua cổng online của trường | cao | _(điền sau khi chạy)_ |  |
| 2 | Học phí được đóng theo học kỳ | Thư viện mở cửa 24/7 | thấp | _(điền sau khi chạy)_ |  |
| 3 | Học bổng khuyến khích học tập cho sinh viên | Sinh viên xét HBKKHT theo GPA | cao | _(điền sau khi chạy)_ |  |
| 4 | Python là ngôn ngữ lập trình bậc cao | Tôi thích ăn phở | thấp | _(điền sau khi chạy)_ |  |
| 5 | BHYT bắt buộc với sinh viên đại học | Bảo hiểm y tế cho người đi học | cao | _(điền sau khi chạy)_ |  |

**Cách chạy** (PowerShell):
```powershell
$env:LAB_SOLUTION_PACKAGE="src.src_Dan_01177"
.venv\Scripts\python.exe
```
```python
from src.chunking import compute_similarity
from src.embeddings import _mock_embed
pairs = [
    ("Sinh viên đăng ký học phần trên cổng học vụ", "SV đăng ký môn học qua cổng online của trường"),
    ("Học phí được đóng theo học kỳ", "Thư viện mở cửa 24/7"),
    ("Học bổng khuyến khích học tập cho sinh viên", "Sinh viên xét HBKKHT theo GPA"),
    ("Python là ngôn ngữ lập trình bậc cao", "Tôi thích ăn phở"),
    ("BHYT bắt buộc với sinh viên đại học", "Bảo hiểm y tế cho người đi học"),
]
for i, (a, b) in enumerate(pairs, 1):
    print(f"Cặp {i}:", compute_similarity(_mock_embed(a), _mock_embed(b)))
```

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> _(điền sau khi chạy — ví dụ: các cặp cùng chủ đề thường cho similarity rất thấp ~0.03 thay vì cao như kỳ vọng, vì mock embedder sinh vector từ hash MD5 của chuời nên không hiểu ngữ nghĩa. Điều này cho thấy mock chỉ phù hợp cho unit test, không phản ánh chất lượng truy xuất — cần model embedding thật (như `paraphrase-multilingual-MiniLM-L12-v2`) cho Giai đoạn 2.)_

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm**.

> 📋 **Nguồn 5 câu hỏi:** xem `REPORT_NHOM.md` Phần 3 → bảng **"Câu hỏi đánh giá & Câu trả lời chuẩn"**. Copy nguyên cột "Câu hỏi (Query)" vào bảng dưới đây (cột 1). Sau khi nhóm thống nhất queries, mỗi thành viên chạy trên code của mình.

> ⏳ **Phần này cần nhóm thống nhất trước:**
> - 1 người convert 7 PDF trong `data/quydinh/` sang `.md` (lưu vào `data/quydinh_md/`)
> - Nhóm thống nhất 5 benchmark queries + gold answers (≥1 cần `metadata_filter={"audience": "student"}`)
> - 5 queries được liệt kê trong `REPORT_NHOM.md` Phần 3
>
> Sau khi có 5 queries, chạy lệnh mẫu:
> ```powershell
> $env:LAB_SOLUTION_PACKAGE="src.src_Dan_01177"
> $env:EMBEDDING_PROVIDER="local"   # dùng embedder đa ngữ nếu đã cài requirements-local.txt
> .venv\Scripts\python.exe
> ```
> ```python
> from ingest import build_knowledge_base
> from src.chunking import RecursiveChunker
> from src.embeddings import LocalEmbedder, _mock_embed
>
> # Chọn embedder
> try:
>     emb = LocalEmbedder()
> except Exception:
>     emb = _mock_embed
>
> # Nạp dữ liệu
> store = build_knowledge_base(
>     "data/quydinh_md",
>     embedding_fn=emb,
>     chunker=RecursiveChunker(chunk_size=500),
> )
> print(f"Loaded {store.get_collection_size()} chunks")
>
> queries = [ ... 5 queries của nhóm ... ]
> for q in queries:
>     print(f"\n=== {q}")
>     for i, r in enumerate(store.search(q, top_k=3), 1):
>         print(f"  [{i}] score={r['score']:.3f} | {r['content'][:80]}...")
> ```

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Sinh viên không thuộc diện cảnh báo học tập được đăng ký tối đa và tối thiểu bao nhiêu tín chỉ trong một học kỳ chính? | _(điền sau khi chạy)_ | _(điền)_ |  | _(điền)_ |
| 2 | Điều kiện để sinh viên được xét học bổng khuyến khích học tập loại A, B và C là gì? | _(điền sau khi chạy)_ | _(điền)_ |  | _(điền)_ |
| 3 | Học phí chương trình đào tạo chuẩn năm học 2025–2026 được quy định như thế nào đối với các ngành Khoa học máy tính và Kỹ thuật hóa học? | _(điền sau khi chạy)_ | _(điền)_ |  | _(điền)_ |
| 4 | Chứng chỉ tiếng Anh dùng để xét miễn học các học phần ngoại ngữ cơ bản phải đáp ứng những điều kiện gì? | _(điền sau khi chạy)_ | _(điền)_ |  | _(điền)_ |
| 5 | Một học phần được coi là tương đương với học phần khác khi đáp ứng điều kiện nào về nội dung chuyên môn và số tín chỉ? | _(điền sau khi chạy)_ | _(điền)_ |  | _(điền)_ |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** __ / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> _(điền sau demo cuối kỳ)_

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | / 5 |
| Hướng tiếp cận của tôi (My Approach) | / 10 |
| Hoàn thiện code (Core Implementation — tests) | / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | / 5 |
| Kết quả truy xuất của tôi (Competition Results) | / 10 |
| **Tổng phần cá nhân** | **/ 60** |
