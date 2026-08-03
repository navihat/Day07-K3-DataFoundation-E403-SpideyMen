# Kết quả Benchmark — Trương Văn Thái (E403-SpideyMen)

- Backend nhúng: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- Corpus: 7 tài liệu trong `data/quydinh/`
- Chiến lược cá nhân: **HeadingChunker** (chia theo Điều/Chương/Phụ lục)

## 1. Baseline — thống kê chunk theo chiến lược

| Chiến lược | Tổng chunk | Độ dài TB | Ngắn nhất | Dài nhất |
|---|---:|---:|---:|---:|
| `fixed_size` | 160 | 888 | 334 | 900 |
| `by_sentences` | 346 | 369 | 67 | 4561 |
| `recursive` | 153 | 837 | 301 | 900 |
| `heading` | 204 | 643 | 120 | 950 |

### ChunkingStrategyComparator trên 2 tài liệu (theo yêu cầu Bài tập 3.1)

| Tài liệu | Chiến lược | count | avg_length |
|---|---|---:|---:|
| hoc-bong-khuyen-khich-hoc-tap | fixed_size | 6 | 891.5 |
| hoc-bong-khuyen-khich-hoc-tap | by_sentences | 17 | 285.94 |
| hoc-bong-khuyen-khich-hoc-tap | recursive | 6 | 814.83 |
| hoc-bong-khuyen-khich-hoc-tap | **heading (của tôi)** | 9 | 550.78 |
| quy-che-dao-tao-5445 | fixed_size | 97 | 894.16 |
| quy-che-dao-tao-5445 | by_sentences | 244 | 317.91 |
| quy-che-dao-tao-5445 | recursive | 91 | 856.2 |
| quy-che-dao-tao-5445 | **heading (của tôi)** | 131 | 613.27 |

## 2. Benchmark — 5 câu hỏi của nhóm, top-3 mỗi chiến lược

### Câu 1: Sinh viên không thuộc diện cảnh báo học tập được đăng ký tối đa và tối thiểu bao nhiêu tín chỉ trong một học kỳ chính?

> Lưu ý: bẫy: đoạn gần giống ở chương thạc sĩ cũng có 24/12 TC

| Chiến lược | # | Score | doc_id | Chunk (rút gọn) | Hit |
|---|---:|---:|---|---|---|
| `fixed_size` | 1 | 0.783 | quy-che-dao-tao-5445 | được phép thực hiện tại đơn vị liên kết hoặc tại ĐHBK Hà Nội. 4. Khối lượng tối đa được cô… |  |
| `fixed_size` | 2 | 0.763 | quy-che-dao-tao-5445 | viên đang bị cảnh báo học tập bị giới hạn khối lượng đăng ký học tập theo quy định tại kho… |  |
| `fixed_size` | 3 | 0.735 | quy-che-dao-tao-5445 | iểm trung bình toàn khóa như xếp loại học lực quy định tại khoản 6 Điều 12 của Quy chế này… |  |
| `by_sentences` | 1 | 0.747 | quy-che-dao-tao-5445 | b) Nâng hai mức cảnh báo học tập đối với sinh viên có số TC không đạt trong học kỳ lớn hơn… |  |
| `by_sentences` | 2 | 0.739 | quy-che-dao-tao-5445 | b) Học viên không đăng ký học tập trong hai học kỳ liên tiếp. c) Học viên bị truy cứu trác… |  |
| `by_sentences` | 3 | 0.735 | quy-che-dao-tao-5445 | c) Điểm trung bình tích lũy toàn khóa đạt từ 2,0 trở lên. 17 d) Tại thời điểm xét tốt nghi… |  |
| `recursive` | 1 | 0.737 | quy-che-dao-tao-5445 | b) Nâng hai mức cảnh báo học tập đối với sinh viên có số TC không đạt trong học kỳ lớn hơn… |  |
| `recursive` | 2 | 0.734 | quy-che-dao-tao-5445 | b) Điểm X: điểm học phần chưa hoàn thiện do thiếu dữ liệu đánh giá. c) Điểm R: điểm học ph… |  |
| `recursive` | 3 | 0.734 | quy-che-dao-tao-5445 | 3. Học viên có đủ các điều kiện sau đây thì được đăng ký xét công nhận tốt nghiệp: a) Đã h… |  |
| `heading` | 1 | 0.774 | quy-che-dao-tao-5445 | Điều 19. Cảnh báo học tập và buộc thôi học — tập này không phụ thuộc vào điều kiện nâng mứ… |  |
| `heading` | 2 | 0.767 | quy-che-dao-tao-5445 | Điều 10. Đăng ký học tập chương trình đại học — b) Sinh viên đang bị cảnh báo học tập bị g… |  |
| `heading` | 3 | 0.725 | quy-che-dao-tao-5445 | Điều 4. Tín chỉ và học phần — số tín chỉ của học phần tương đương tối thiểu bằng hoặc lớn … |  |

### Câu 2: Điều kiện để sinh viên được xét học bổng khuyến khích học tập loại A, B và C là gì?

| Chiến lược | # | Score | doc_id | Chunk (rút gọn) | Hit |
|---|---:|---:|---|---|---|
| `fixed_size` | 1 | 0.839 | hoc-bong-khuyen-khich-hoc-tap | khóa, ngành đào tạo theo thứ tự ưu tiên từ loại A đến loại C cho đến khi hết quỹ học bổng.… |  |
| `fixed_size` | 2 | 0.740 | hoc-bong-khuyen-khich-hoc-tap | 18/NQ-ĐHBK ngày 02 tháng 10 năm 2020 của Hội đồng Trường. 2. Quy định này áp dụng đối với … |  |
| `fixed_size` | 3 | 0.730 | hoc-bong-khuyen-khich-hoc-tap | các học phần không tính điểm GPA) tại học kỳ cấp học bổng; g) Học quá thời gian thiết kế c… |  |
| `by_sentences` | 1 | 0.823 | hoc-bong-khuyen-khich-hoc-tap | Khuyến khích và ưu tiên hình thức cấp kinh phí hỗ trợ (tương đương với mức học bổng) gắn v… |  |
| `by_sentences` | 2 | 0.797 | hoc-bong-khuyen-khich-hoc-tap | Các quy định chung 1. Học bổng khuyến khích học tập (KKHT) cấp cho các sinh viên được lựa … |  |
| `by_sentences` | 3 | 0.782 | hoc-bong-khuyen-khich-hoc-tap | Nguyên tắc xét cấp học bổng 2 1. Sử dụng kết quả học tập và rèn luyện của học kỳ liền trướ… |  |
| `recursive` | 1 | 0.819 | hoc-bong-khuyen-khich-hoc-tap | học bổng) gắn với các chương trình trao đổi sinh viên trong và ngoài nước, các khóa học nâ… |  |
| `recursive` | 2 | 0.769 | hoc-bong-khuyen-khich-hoc-tap | 2. Quy định này áp dụng đối với sinh viên hệ đại học của Trường ĐHBK Hà Nội. Điều 2. Các q… |  |
| `recursive` | 3 | 0.739 | hoc-bong-khuyen-khich-hoc-tap | i) Sinh viên thuộc các chương trình chuyển hệ đào tạo. Điều 5. Thời gian công bố kết quả x… |  |
| `heading` | 1 | 0.759 | hoc-bong-khuyen-khich-hoc-tap | Điều 4. Nguyên tắc xét cấp học bổng — 2 1. Sử dụng kết quả học tập và rèn luyện của học kỳ… |  |
| `heading` | 2 | 0.747 | hoc-bong-khuyen-khich-hoc-tap | Điều 2. Các quy định chung — 1. Học bổng khuyến khích học tập (KKHT) cấp cho các sinh viên… |  |
| `heading` | 3 | 0.714 | hoc-bong-khuyen-khich-hoc-tap | Điều 2. Các quy định chung — c) Học bổng loại xuất sắc (loại A): Bằng 1,5 lần mức học bổng… | ✅ |

### Câu 3: Học phí chương trình đào tạo chuẩn năm học 2025-2026 được quy định như thế nào đối với các ngành Khoa học máy tính và Kỹ thuật hóa học?

> Lưu ý: gold answer nằm trong BẢNG ở Phụ lục I

| Chiến lược | # | Score | doc_id | Chunk (rút gọn) | Hit |
|---|---:|---:|---|---|---|
| `fixed_size` | 1 | 0.739 | quy-dinh-hoc-phi-2025-2026 | học và sau đại học đối với năm học 2025-2026; Theo đề nghị của ông Trưởng Ban Đào tạo. QUY… |  |
| `fixed_size` | 2 | 0.722 | quy-che-dao-tao-5445 | (Ban hành kèm theo Quyết định số /QĐ-ĐHBK, ngày tháng năm 2025 của Giám đốc Đại học Bách k… |  |
| `fixed_size` | 3 | 0.716 | quy-che-dao-tao-5445 | i học; Căn cứ Thông tư số 18/2021/TT-BGDĐT ngày 28 tháng 06 năm 2021 của Bộ Giáo dục và Đà… |  |
| `by_sentences` | 1 | 0.733 | quy-che-dao-tao-5445 | 2. Quy chế này được áp dụng từ học kỳ 1 năm học 2025-2026 cho tất cả các khóa đào tạo, trừ… |  |
| `by_sentences` | 2 | 0.732 | quy-che-dao-tao-5445 | 4 Danh mục thống kê ngành đào tạo của giáo dục đại học ban hành theo Thông tư số 09/2022/T… |  |
| `by_sentences` | 3 | 0.708 | quy-che-dao-tao-5445 | c) Khoản 2 Điều 18 (về việc học cùng lúc hai chương trình) được áp dụng với các khóa tuyển… |  |
| `recursive` | 1 | 0.757 | quy-che-dao-tao-5445 | dục và Đào tạo ban hành Quy chế tuyển sinh và đào tạo trình độ tiến sĩ; Căn cứ Thông tư số… |  |
| `recursive` | 2 | 0.754 | quy-dinh-hoc-phi-2025-2026 | Điều 1. Phê duyệt mức học phí các chương trình đào tạo đại học chính quy, đào tạo kỹ sư ch… |  |
| `recursive` | 3 | 0.736 | quy-che-dao-tao-5445 | học tập tối đa không quá 50% tổng khối lượng của các học phần tiến sĩ trong CTĐT. 30 CHƯƠN… |  |
| `heading` | 1 | 0.767 | quy-che-dao-tao-5445 | dục và Đào tạo ban hành Quy chế tuyển sinh và đào tạo trình độ tiến sĩ; Căn cứ Thông tư số… |  |
| `heading` | 2 | 0.729 | quy-dinh-hoc-phi-2025-2026 | Phụ lục I — MỨC HỌC PHÍ CÁC CHƯƠNG TRÌNH ĐÀO TẠO ĐẠI HỌC CHÍNH QUY, KỸ SƯ CHUYÊN SÂU, VỪA … | ✅ |
| `heading` | 3 | 0.726 | quy-dinh-hoc-phi-2025-2026 | Điều 1. Phê duyệt mức học phí các chương trình đào tạo đại học chính quy, đào tạo kỹ sư — … |  |

### Câu 4: Chứng chỉ tiếng Anh dùng để xét miễn học các học phần ngoại ngữ cơ bản phải đáp ứng những điều kiện gì?

> Lưu ý: gold answer trải trên Điều 3 VÀ Phụ lục II

| Chiến lược | # | Score | doc_id | Chunk (rút gọn) | Hit |
|---|---:|---:|---|---|---|
| `fixed_size` | 1 | 0.767 | quy-che-dao-tao-5445 | ác do Bộ Giáo dục và Đào tạo quy định, hoặc bằng tốt nghiệp trình độ đại học trở lên ngành… |  |
| `fixed_size` | 2 | 0.750 | quy-dinh-ngoai-ngu-k70 | hập học. Việc lựa chọn tiêu chí phân lo ại trong số các tiêu chí trên do Giám đốc Đại học … |  |
| `fixed_size` | 3 | 0.728 | quy-dinh-ngoai-ngu-k70 | uẩn ngoại ngữ yêu cầu đối với sinh viên đại học hình thức chính quy (Kèm theo Quyết định s… | ✅ |
| `by_sentences` | 1 | 0.808 | quy-dinh-ngoai-ngu-k70 | Điều 2. Phân loại trình độ đầu vào và phân lớp học ngoại ngữ cơ bản 1. Căn cứ phân loại tr… | ✅ |
| `by_sentences` | 2 | 0.769 | quy-dinh-ngoai-ngu-k70 | Việc lựa chọn tiêu chí phân lo ại trong số các tiêu chí trên do Giám đốc Đại học Bách khoa… |  |
| `by_sentences` | 3 | 0.730 | quy-dinh-ngoai-ngu-k70 | 2. Điều kiện xét quy đổi tương đương chứng chỉ và miễn học - Kết quả bài kiểm tra TOEIC Pl… | ✅ |
| `recursive` | 1 | 0.777 | quy-dinh-ngoai-ngu-k70 | 1. Yêu cầu về chuẩn ngoại ngữ đầu ra được quy định cụ thể cho từng CTĐT tại các Phụ lục tư… | ✅ |
| `recursive` | 2 | 0.771 | quy-dinh-ngoai-ngu-k70 | học các CTĐT có ngôn ng ữ giảng dạy khác ti ếng Việt, việc xét mi ễn/áp dụng NNCB thực hiệ… | ✅ |
| `recursive` | 3 | 0.699 | quy-dinh-ngoai-ngu-k70 | ngoại ngữ của sinh viên được tăng cường dần qua các học kỳ và được quy định như sau: 1. Tr… |  |
| `heading` | 1 | 0.799 | quy-dinh-ngoai-ngu-k70 | Điều 2. Phân loại trình độ đầu vào và phân lớp học ngoại ngữ cơ bản — 1. Căn cứ phân loại … | ✅ |
| `heading` | 2 | 0.760 | quy-dinh-ngoai-ngu-k70 | Điều 5. Yêu cầu về chuẩn ngoại ngữ đầu ra — 1. Yêu cầu về chuẩn ngoại ngữ đầu ra được quy … | ✅ |
| `heading` | 3 | 0.732 | quy-dinh-ngoai-ngu-k70 | Điều 4. Lộ trình học tập các học phần ngoại ngữ cơ bản — Lộ trình học tập đối với các học … |  |

### Câu 5: Một học phần được coi là tương đương với học phần khác khi đáp ứng điều kiện nào về nội dung chuyên môn và số tín chỉ?

| Chiến lược | # | Score | doc_id | Chunk (rút gọn) | Hit |
|---|---:|---:|---|---|---|
| `fixed_size` | 1 | 0.765 | quy-che-dao-tao-5445 | n theo mô đun: người học chọn một định hướng chuyên môn và phải hoàn thành tất cả học phần… | ✅ |
| `fixed_size` | 2 | 0.721 | quy-che-dao-tao-5445 | được phép thực hiện tại đơn vị liên kết hoặc tại ĐHBK Hà Nội. 4. Khối lượng tối đa được cô… |  |
| `fixed_size` | 3 | 0.709 | quy-che-dao-tao-5445 | ay thế được trường/khoa/viện chỉ định để lấy kết quả thay cho một học phần yêu cầu trong c… |  |
| `by_sentences` | 1 | 0.817 | quy-che-dao-tao-5445 | Học phần tương đương và học phần thay thế a) Hai học phần được coi là tương đương khi có n… | ✅ |
| `by_sentences` | 2 | 0.740 | quy-che-dao-tao-5445 | b) Người học được phép học một học phần thay thế được trường/khoa/viện chỉ định để lấy kết… |  |
| `by_sentences` | 3 | 0.717 | quy-che-dao-tao-5445 | b) Đối với CTĐT thạc sĩ và tiến sĩ: từ điểm C trở lên. 8. Người học có thể đăng ký học lại… |  |
| `recursive` | 1 | 0.809 | quy-che-dao-tao-5445 | a) Hai học phần được coi là tương đương khi có nội dung chuyên môn trùng lặp tối thiểu 70%… | ✅ |
| `recursive` | 2 | 0.710 | quy-che-dao-tao-5445 | viên phải hoàn thành học phần A (với mức điểm đạt) mới được dự lớp học phần B. b) Học phần… |  |
| `recursive` | 3 | 0.706 | quy-che-dao-tao-5445 | b) Điểm X: điểm học phần chưa hoàn thiện do thiếu dữ liệu đánh giá. c) Điểm R: điểm học ph… |  |
| `heading` | 1 | 0.811 | quy-che-dao-tao-5445 | Điều 4. Tín chỉ và học phần — số tín chỉ của học phần tương đương tối thiểu bằng hoặc lớn … |  |
| `heading` | 2 | 0.703 | quy-che-dao-tao-5445 | Điều 11. Công nhận kết quả học tập và chuyển đổi tín chỉ — 1. Kết quả học tập của người họ… |  |
| `heading` | 3 | 0.697 | quy-che-dao-tao-5445 | Điều 2. Ngành đào tạo, chương trình đào tạo — sáng tạo, đáp ứng yêu cầu nhân lực chất lượn… |  |

### Bảng điểm tổng (tự động, theo docs/SCORING.md: top-1 đúng = 2đ, top-2/3 = 1đ)

| Chiến lược | Điểm /10 |
|---|---:|
| `by_sentences` | 4 |
| `recursive` | 4 |
| `heading` | 4 |
| `fixed_size` | 3 |

## 3. A/B metadata filter (chiến lược heading)

Câu hỏi: *Sinh viên nộp hồ sơ ở đâu và cần giấy tờ gì để được xác nhận kết quả học tập?*

**search() — không lọc**

| # | Score | doc_id | audience | Chunk (rút gọn) |
|---:|---:|---|---|---|
| 1 | 0.652 | quy-che-dao-tao-5445 | student | Điều 14. Đăng ký tốt nghiệp đại học — xét công nhận tốt nghiệp. 6. Sin… |
| 2 | 0.628 | quy-che-dao-tao-5445 | student | Điều 29. Đăng ký đề tài luận văn thạc sĩ — 1. Học viên thực hiện đăng … |
| 3 | 0.625 | quy-che-dao-tao-5445 | student | Điều 34. Điều kiện tốt nghiệp thạc sĩ và xếp hạng tốt nghiệp — 1. Học … |

**search_with_filter(audience="student")**

| # | Score | doc_id | audience | Chunk (rút gọn) |
|---:|---:|---|---|---|
| 1 | 0.652 | quy-che-dao-tao-5445 | student | Điều 14. Đăng ký tốt nghiệp đại học — xét công nhận tốt nghiệp. 6. Sin… |
| 2 | 0.628 | quy-che-dao-tao-5445 | student | Điều 29. Đăng ký đề tài luận văn thạc sĩ — 1. Học viên thực hiện đăng … |
| 3 | 0.625 | quy-che-dao-tao-5445 | student | Điều 34. Điều kiện tốt nghiệp thạc sĩ và xếp hạng tốt nghiệp — 1. Học … |

## 4. KnowledgeBaseAgent — kiểm tra grounding

```
[prompt 3262 ký tự, 3 chunk ngữ cảnh]
```

