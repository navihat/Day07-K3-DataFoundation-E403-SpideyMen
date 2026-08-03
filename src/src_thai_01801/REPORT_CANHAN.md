# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Trương Văn Thái
**Nhóm:** Spideymen
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `report/REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.
>
> File này đặt trong `src/src_thai_01801/` theo quy ước của nhóm (mỗi thành viên một package riêng) để không ghi đè báo cáo của thành viên khác trong `report/REPORT_CANHAN.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Cosine đo **góc** giữa hai vector embedding chứ không đo khoảng cách. Điểm càng gần 1 nghĩa là hai vector càng cùng hướng, tức mô hình đặt hai đoạn văn bản vào cùng một "vùng ý nghĩa". Điểm quanh 0 là không liên quan, điểm âm là ngược hướng (hiếm gặp với embedding văn bản thực tế vì các vector thường nằm trong một nón hẹp).

**Ví dụ có độ tương tự CAO:** *(số đo thật, xem Phần 4 cặp 1)*
- Câu A: "Sinh viên được đăng ký tối đa bao nhiêu tín chỉ trong một học kỳ?"
- Câu B: "Số tín chỉ tối đa mà sinh viên được phép đăng ký trong học kỳ chính"
- Tại sao tương đồng: cùng đối tượng (sinh viên), cùng đại lượng hỏi (số tín chỉ tối đa), cùng phạm vi (học kỳ chính) — chỉ khác cách diễn đạt. **Đo được 0,787.**

**Ví dụ có độ tương tự THẤP:** *(số đo thật, xem Phần 4 cặp 2)*
- Câu A: "Thời hạn nộp học phí của sinh viên là khi nào?"
- Câu B: "Điều kiện xét cấp học bổng khuyến khích học tập loại A"
- Tại sao khác: cùng thuộc miền quy định đại học và cùng nói về sinh viên, nhưng khác hẳn chủ đề (nghĩa vụ tài chính vs. quyền lợi khen thưởng) và khác loại thông tin (thời hạn vs. tiêu chuẩn). **Đo được 0,388.**

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Vì độ dài vector embedding phụ thuộc vào **độ dài văn bản**, còn thứ ta quan tâm là **chủ đề**. Một chunk 900 ký tự và một câu hỏi 20 từ có thể nói cùng một điều nhưng magnitude rất khác nhau; Euclid sẽ coi chúng xa nhau chỉ vì chênh lệch độ dài, còn cosine bỏ qua magnitude và chỉ so hướng. Thực tế trong lab này thấy rõ: chunk trong `EmbeddingStore` dài gấp hàng chục lần query nhưng vẫn được xếp hạng đúng.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**

> Bước nhảy mỗi lần trượt cửa sổ: `step = chunk_size − overlap = 500 − 50 = 450`.
> Áp dụng công thức: `ceil((10000 − 50) / 450) = ceil(9950 / 450) = ceil(22,11) = 23`
> **Đáp án: 23 chunks.**
>
> Tôi đã kiểm chứng lại bằng chính code của mình chứ không chỉ tính tay:
> ```python
> len(FixedSizeChunker(chunk_size=500, overlap=50).chunk("x" * 10000))  # -> 23
> ```
> Kết quả khớp công thức. Chunk cuối chỉ dài 100 ký tự (phần dư), không phải 500.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**

> `step` giảm còn 400 → `ceil((10000 − 100) / 400) = ceil(24,75) = 25 chunks` (code cũng trả về **25**). Tăng khoảng 9%.
>
> Lý do muốn overlap lớn hơn: câu trả lời thường nằm vắt qua ranh giới chunk. Với văn bản quy định của nhóm tôi, một điều khoản hay có dạng "điều kiện… thì… trừ trường hợp…"; nếu ranh giới rơi đúng vào giữa thì cả hai chunk đều trả lời sai. Overlap tạo vùng đệm để ít nhất một chunk chứa trọn ý.
>
> Cái giá phải trả: số chunk tăng → tốn chi phí nhúng và lưu trữ, đồng thời các chunk trùng lặp nhau có thể **chiếm nhiều slot trong top-k**, đẩy chunk khác thực sự liên quan ra ngoài. Đây chính là lý do tôi chọn hướng khác cho Giai đoạn 2: thay vì tăng overlap, tôi cắt theo **ranh giới ngữ nghĩa có sẵn của văn bản** (Điều/Chương/Phụ lục) để ý không bao giờ bị cắt ngang ngay từ đầu.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Mã nguồn: `src/src_thai_01801/`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng một regex duy nhất `(?<=[.!?])\s+` — lookbehind nên dấu kết câu được **giữ lại** ở cuối câu trước, còn `\s+` nuốt trọn cả khoảng trắng lẫn xuống dòng nên bắt được cả 4 trường hợp đề bài yêu cầu (`". "`, `"! "`, `"? "`, `".\n"`) mà không cần liệt kê riêng. Sau khi tách thì `strip()` từng câu và loại câu rỗng, rồi gom theo bước nhảy `max_sentences_per_chunk`. Edge case xử lý: text rỗng hoặc toàn khoảng trắng trả `[]`; `max(1, ...)` trong `__init__` chặn tham số 0 hoặc âm gây chia nhóm vô hạn.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> `_split` có **ba base case**: chuỗi rỗng → `[]`; chuỗi đã ngắn hơn `chunk_size` → `[text]`; hết separator (hoặc gặp separator `""`) → cắt cứng theo `chunk_size`. Phần đệ quy: thử separator đầu danh sách, nếu văn bản **không chứa** separator đó thì gọi lại chính nó với separator kế tiếp (nhờ vậy `separators=[]` vẫn chạy an toàn). Nếu có thì split rồi **gộp tham lam** các mảnh trở lại — nối bằng đúng separator gốc để không mất ký tự — cho tới sát `chunk_size`; mảnh nào vẫn quá lớn thì đệ quy tiếp với separator nhỏ hơn. Điểm tôi chú ý là *gộp lại sau khi split*: nếu chỉ split mà không gộp thì văn bản nhiều dòng ngắn sẽ vỡ thành hàng trăm chunk vụn.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> `_make_record` chuẩn hóa mỗi `Document` thành `{id, content, metadata, embedding}` với **id nội bộ tự sinh** từ bộ đếm `_next_index`, không dùng `doc.id`. Lý do: test thêm hai lần cùng một danh sách `doc0..doc2` và kỳ vọng size = 5 chứ không phải 3 — nếu lấy `doc.id` làm khóa thì ChromaDB sẽ upsert đè lên nhau. `_make_record` cũng `setdefault("doc_id", doc.id)` để `delete_document`/lọc metadata vẫn chạy được với document không có metadata. `search` embed query rồi tính **dot product** qua `_dot` — các embedder trong lab (mock, MiniLM, OpenAI) đều trả vector đã chuẩn hóa nên dot chính là cosine — sort giảm dần, cắt `top_k`.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Lọc **trước**, search **sau**. Lý do không làm ngược lại: nếu search top-k rồi mới lọc thì bộ lọc có thể xóa sạch kết quả và trả về ít hơn `top_k` dù kho vẫn còn chunk hợp lệ. `metadata_filter` rỗng/`None` được ủy quyền thẳng cho `search()` để hai đường cho cùng số lượng kết quả. `delete_document` lọc bỏ mọi record có `metadata['doc_id']` khớp rồi so độ dài trước/sau để quyết định trả `True`/`False` — cách này xử lý được cả document nhiều chunk (do `ingest.py` sinh ra) lẫn document đơn lẻ.
>
> Tôi có viết sẵn cả nhánh ChromaDB (EphemeralClient, `hnsw:space=cosine`, `score = 1 − distance`, `$and` cho filter nhiều khóa) nhưng nó chỉ kích hoạt khi môi trường có `chromadb`; mặc định lab chạy nhánh in-memory.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Ba bước: retrieve `top_k` chunk → dựng prompt → gọi `llm_fn`. Prompt đánh số từng chunk kèm **nguồn** (`source_url` → `source` → `doc_id`) và **score**, để khi đọc câu trả lời còn truy được nó dựa vào đoạn nào — chính là tiêu chí "Source Traceability" trong `docs/EVALUATION.md`. Phần chỉ dẫn nói rõ chỉ được dùng thông tin trong ngữ cảnh và phải báo không tìm thấy thay vì suy đoán. Nếu `search()` trả rỗng thì tôi **không gọi LLM** mà trả thẳng câu "Không tìm thấy thông tin liên quan…" — gọi LLM với ngữ cảnh rỗng là mời nó bịa.

### Chiến lược riêng cho Giai đoạn 2: `HeadingChunker`

> Ngoài 4 lớp bắt buộc, tôi viết thêm `HeadingChunker` — chia văn bản theo ranh giới `Điều` / `Chương` / `Phụ lục` và **ghép tiêu đề Điều vào nội dung mọi chunk con**. Lý do và bằng chứng số liệu ở Phần 5.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

### Kết Quả Kiểm Thử (Test Results)

```
$ LAB_SOLUTION_PACKAGE=src.src_thai_01801 pytest tests/ -q
....................................................                     [100%]
52 passed in 0.11s
```

**Số lượng bài test vượt qua (pass):** **42 / 42**

10 test còn lại là bộ test tôi tự viết cho `HeadingChunker` ở `tests/test_heading_chunker.py`,
tách riêng khỏi `tests/test_solution.py` để không đụng vào bộ test được chấm.

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Chạy bằng embedder thật `paraphrase-multilingual-MiniLM-L12-v2` (384 chiều) chứ không dùng
mock, vì mock sinh vector từ hash MD5 nên điểm gần như ngẫu nhiên và không nói lên điều gì
về ngữ nghĩa. Dự đoán được ghi **trước** khi chạy. Ngưỡng phân loại: ≥ 0,70 là "cao".
Script: `scripts/similarity_predictions.py`.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên được đăng ký tối đa bao nhiêu tín chỉ trong một học kỳ? | Số tín chỉ tối đa mà sinh viên được phép đăng ký trong học kỳ chính | cao | **0,787** | ✅ |
| 2 | Thời hạn nộp học phí của sinh viên là khi nào? | Điều kiện xét cấp học bổng khuyến khích học tập loại A | thấp | **0,388** | ✅ |
| 3 | Sinh viên được đăng ký tối đa 24 TC trong học kỳ chính. | **Học viên** được đăng ký tối đa 24 TC trong một học kỳ chính. | cao | **0,998** | ✅ |
| 4 | Sinh viên đăng ký tối đa 24 **tín chỉ** trong học kỳ chính. | Sinh viên đăng ký tối đa 24 **TC** trong học kỳ chính. | cao | **0,829** | ✅ |
| 5 | Chuẩn ngoại ngữ đầu ra đối với sinh viên K70 | Quy định về chứng chỉ tiếng Anh để xét miễn học phần ngoại ngữ | cao | **0,566** | ❌ |

**Đúng 4/5.** Cặp 3 và 4 không chọn ngẫu nhiên — tôi thiết kế chúng để kiểm chứng hai giả
thuyết đặt ra *trước* khi chạy benchmark, và cả hai đều ảnh hưởng trực tiếp tới thiết kế
chunker của tôi.

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**

> Bất ngờ nhất là **cặp 3 đạt 0,998** — gần như trùng khít. Hai câu chỉ khác đúng một từ chỉ
> đối tượng ("sinh viên" / "học viên"), nhưng về mặt pháp lý là hai quy định của hai bậc học
> khác nhau, và Quy chế đào tạo của trường có **cả hai câu gần giống hệt nhau** ở hai chương
> khác nhau. Nghĩa là: **nội dung chunk một mình không đủ để phân biệt chúng** — embedding
> "nhìn" thấy chủ đề (đăng ký tín chỉ) nhưng gần như mù với chi tiết phân biệt đối tượng.
> Đây chính là lý do tôi quyết định ghép tiêu đề Điều vào chunk: cụm "chương trình đại học"
> trong tiêu đề tạo ra tín hiệu phân biệt mà thân văn bản không có.
>
> Cặp 4 (0,829) cho tin vui ngược lại: model bắc được cầu giữa "tín chỉ" và viết tắt "TC" —
> việc mà tìm kiếm từ khóa hoàn toàn bó tay. Điều này quan trọng vì văn bản gốc gần như luôn
> viết "24 TC" trong khi câu hỏi của nhóm viết "bao nhiêu tín chỉ".
>
> Cặp 5 là dự đoán **sai** của tôi: tôi nghĩ "chuẩn ngoại ngữ đầu ra" và "chứng chỉ tiếng Anh
> xét miễn học phần" đủ gần để trên 0,70, nhưng chỉ được 0,566. Bài học: embedding nhạy với
> **khác biệt về hành động** (đầu ra vs. miễn học) hơn là tôi tưởng, dù hai câu cùng chủ đề
> ngoại ngữ. Nói cách khác, "cùng chủ đề" không đồng nghĩa với "cùng ý định truy vấn".

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

**Chiến lược của tôi:** `HeadingChunker` — cắt theo ranh giới `Điều` / `Chương` / `Phụ lục`,
ghép tiêu đề Điều vào nội dung mọi chunk con (`min_chunk_size=120`, `max_chunk_size=900`).
**Corpus:** 7 file `.md` của nhóm trong `data/quydinh/`. **Embedder:** `paraphrase-multilingual-MiniLM-L12-v2`.
**Câu hỏi:** đúng 5 câu nhóm thống nhất. Kết quả đầy đủ: `report/benchmark_results.md`.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Tối đa/tối thiểu bao nhiêu tín chỉ trong một học kỳ chính? | *Điều 19. Cảnh báo học tập và buộc thôi học* | 0,774 | ❌ Sai Điều | Nói về cảnh báo học tập, không có ngưỡng 24/12 TC |
| 2 | Điều kiện xét học bổng KKHT loại A, B, C? | *Điều 4. Nguyên tắc xét cấp học bổng* | 0,759 | ⚠️ Top-1 sai, **top-3 đúng** (*Điều 2*, 0,714 — có ngưỡng loại A/B/C) | Nêu được mức phân loại học bổng |
| 3 | Học phí ngành KHMT và KTHH 2025-2026? | *Quy chế đào tạo — căn cứ ban hành* | 0,767 | ⚠️ Top-1 sai, **top-2 đúng** (*Phụ lục I — Mức học phí*, 0,729) | Lấy được bảng mức học phí ở vị trí 2 |
| 4 | Chứng chỉ tiếng Anh xét miễn học phần cần điều kiện gì? | *Điều 2. Phân loại trình độ đầu vào và phân lớp học ngoại ngữ cơ bản* | 0,799 | ✅ Đúng, top-1 (top-2 *Điều 5* cũng đúng) | Nêu điều kiện chứng chỉ và quy đổi tương đương |
| 5 | Khi nào hai học phần được coi là tương đương? | *Điều 4. Tín chỉ và học phần* — "…số tín chỉ của học phần tương đương…" | 0,811 | ⚠️ Đúng Điều, chứa **nửa sau** gold answer (điều kiện tín chỉ) nhưng thiếu ngưỡng 70% | Trả lời được phần điều kiện tín chỉ |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **3 / 5** (câu 2, 3, 4 — theo
kiểm tra từ khóa tự động). Nếu chấm tay thì câu 5 cũng tính là một phần vì chunk top-1 đúng
Điều 4 và chứa một nửa gold answer, chỉ mất ngưỡng "70%" do Điều 4 dài hơn `max_chunk_size`
nên bị cắt làm hai.

### So sánh với 3 chiến lược cơ sở (cùng corpus, cùng 5 câu hỏi, cùng embedder)

| Chiến lược | Tổng chunk | Độ dài TB | Điểm /10 | Số câu có chunk đúng trong top-3 |
|---|---:|---:|---:|---:|
| **`heading` (của tôi)** | 204 | 643 | 4 | **3 / 5** (câu 2, 3, 4) |
| `by_sentences` (3 câu) | 346 | 369 | 4 | 2 / 5 (câu 4, 5) |
| `recursive` (900) | 153 | 837 | 4 | 2 / 5 (câu 4, 5) |
| `fixed_size` (900/90) | 160 | 888 | 3 | 2 / 5 (câu 4, 5) |

**Kết quả trung thực: bốn chiến lược gần như hòa nhau về điểm, nhưng khác nhau về *kiểu* thành công.**
Ba baseline chỉ ghi điểm ở hai câu dễ (4 và 5) và ghi ở vị trí top-1. `HeadingChunker` là
chiến lược **duy nhất** chạm được câu 2 và câu 3 — hai câu mà cả ba baseline đều trả về rỗng
hoàn toàn trong top-3 — nhưng lại đặt chúng ở hạng 2-3 nên chỉ được 1 điểm mỗi câu theo
`docs/SCORING.md`. Nói cách khác: cách chấm thưởng cho việc *xếp đúng ở hạng 1*, nên một
chiến lược tìm được câu trả lời khó ở hạng 2 bị tính ngang với chiến lược bỏ trắng câu đó.
Nếu đo bằng **độ phủ** (bao nhiêu câu có chunk đúng trong top-3) thì `heading` hơn hẳn: 3/5
so với 2/5.

### Phân tích thất bại

**Câu 1 — cả 4 chiến lược đều trượt.** Đây là thất bại đáng chú ý nhất. Câu hỏi chứa cụm
"**không thuộc diện cảnh báo học tập**", và cụm đó kéo mọi chiến lược về *Điều 19. Cảnh báo
học tập và buộc thôi học* thay vì *Điều 10. Đăng ký học tập*. Từ khóa phụ trong câu hỏi mạnh
hơn ý chính. Ngoài ra còn hai yếu tố tôi đã dự đoán trước ở Phần 4: (a) văn bản viết "24 TC"
còn câu hỏi viết "tín chỉ" (cặp 4 cho thấy model bắc cầu được nhưng không hoàn hảo); (b) Quy
chế có **hai đoạn gần như giống hệt** cho sinh viên và học viên cao học (cặp 3: **0,998**),
làm loãng tín hiệu. Hướng sửa: viết lại câu hỏi bỏ mệnh đề phụ, hoặc mở rộng truy vấn
(query expansion) thêm biến thể "TC".

**Câu 3 — bảng số liệu khó truy xuất.** Gold answer nằm trong *Phụ lục I*, là một **bảng**
mức học phí theo ngành, gần như không có câu văn tự nhiên. `HeadingChunker` lấy được nó ở
hạng 2 nhờ giữ nguyên tiêu đề "Phụ lục I — MỨC HỌC PHÍ…" làm tín hiệu văn bản; ba baseline
không có tiêu đề trong chunk nên trượt hẳn. Đây là bằng chứng trực tiếp cho quyết định ghép
tiêu đề vào chunk. Muốn tốt hơn nữa thì phải chuyển bảng thành câu ("Ngành Khoa học máy tính:
630.000 đồng/tín chỉ") hoặc dùng hybrid search kết hợp từ khóa.

**Câu 5 — chunk bị cắt đúng chỗ hiểm.** Điều 4 dài hơn `max_chunk_size=900` nên bị chia đôi;
ngưỡng "70%" rơi vào mảnh này, điều kiện tín chỉ rơi vào mảnh kia. Cả hai mảnh đều mang tiêu
đề "Điều 4. Tín chỉ và học phần" nên vẫn truy vết được, nhưng không mảnh nào chứa trọn gold
answer. Hướng sửa: tăng `max_chunk_size` hoặc cho các mảnh con của cùng một Điều chồng lấn nhau.

### Metadata filter — không kiểm chứng được trên corpus hiện tại

| | Top-1 | audience |
|---|---|---|
| `search()` không lọc | *Điều 14. Đăng ký tốt nghiệp đại học* (0,652) | student |
| `search_with_filter(audience="student")` | *Điều 14. Đăng ký tốt nghiệp đại học* (0,652) | student |

Hai bảng **giống hệt nhau**. Lý do: cả 7 tài liệu trong corpus đều gán `audience: student`,
nên bộ lọc không loại được gì. Đây là một vấn đề cần báo với nhóm — `K3_VARIANT.md` yêu cầu
**ít nhất một câu hỏi phải cần** `metadata_filter={"audience": "student"}` mới trả lời đúng,
mà điều đó chỉ chứng minh được nếu corpus có tài liệu thuộc `audience` khác (`faculty`/`staff`/`all`)
để bị loại ra. Đề xuất: bổ sung một văn bản công khai dành cho cán bộ/giảng viên, hoặc gán
lại `audience: all` cho *Quy định hành chính sinh viên* nếu đọc kỹ thấy nó áp dụng cho cả cán
bộ (bản PDF gốc `QD_Hanh_chinh.pdf` nêu đối tượng thi hành gồm cả "cán bộ viên chức" lẫn
"sinh viên").

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *(điền sau buổi demo)*

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 8 / 10 |
| **Tổng phần cá nhân** | **58 / 60** |

*Tự trừ 2 điểm ở mục Kết quả truy xuất: chỉ 3/5 câu có chunk đúng trong top-3, và câu 1 thất
bại trên cả bốn chiến lược.*

---

## Ghi chú gửi nhóm

1. **`REPORT_NHOM.md` Phần 2 ghi chiến lược của tôi là `SentenceChunker(max_sentences=3)`, 8/10.**
   Con số đó không khớp với thực tế đo được. Chiến lược tôi thực sự làm là `HeadingChunker`
   (chia theo Điều/Chương/Phụ lục), đo trên corpus của nhóm được **4/10** theo cách chấm
   top-1, hoặc **3/5 câu có chunk đúng trong top-3**. Nhóm nên sửa lại bảng đó cho khớp —
   `SentenceChunker` để nguyên tham số mặc định là một trong ba baseline, không phải chiến
   lược riêng của thành viên nào.

2. **`REPORT_NHOM.md` Phần 3 — bảng "Câu hỏi đánh giá & Câu trả lời chuẩn" đang trống.**
   Năm câu hỏi đã từng có ở commit `f254e9f` nhưng bị mất trong một lần commit sau đó. Nội
   dung cũ vẫn lấy lại được bằng `git show f254e9f -- report/REPORT_NHOM.md`.

3. **Bảng "Tổng hợp chất lượng truy xuất" ở Phần 3 đang liệt kê 5 câu hỏi khác** (chuẩn đầu
   ra ngoại ngữ, mức hỗ trợ BHYT, giấy xác nhận sinh viên…) so với 5 câu benchmark thật.
   Hai danh sách này cần thống nhất, nếu không phần chấm 10 điểm Retrieval Quality sẽ không
   đối chiếu được.

4. **Chưa có câu hỏi nào cần `audience` filter** và corpus chưa có tài liệu `audience` khác
   `student` — xem phân tích cuối Phần 5.

**Tái lập kết quả trong báo cáo này:**
```bash
EMBEDDING_PROVIDER=local python3 scripts/run_benchmark.py          # Phần 5
EMBEDDING_PROVIDER=local python3 scripts/similarity_predictions.py # Phần 4
LAB_SOLUTION_PACKAGE=src.src_thai_01801 pytest tests/ -q           # Phần 3
```
