# Kết quả Benchmark — Trương Văn Thái (E403-SpideyMen)

- Backend nhúng: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- Corpus: 6 tài liệu trong `data/quydinh/`
- Chiến lược cá nhân: **HeadingChunker** (chia theo Điều/Chương/Phụ lục)

## 1. Baseline — thống kê chunk theo chiến lược

| Chiến lược | Tổng chunk | Độ dài TB | Ngắn nhất | Dài nhất |
|---|---:|---:|---:|---:|
| `fixed_size` | 170 | 885 | 241 | 900 |
| `by_sentences` | 335 | 402 | 55 | 5452 |
| `recursive` | 189 | 715 | 1 | 900 |
| `heading` | 232 | 635 | 10 | 898 |

### ChunkingStrategyComparator trên 2 tài liệu (theo yêu cầu Bài tập 3.1)

| Tài liệu | Chiến lược | count | avg_length |
|---|---|---:|---:|
| hoc-bong-kkht | fixed_size | 6 | 897.5 |
| hoc-bong-kkht | by_sentences | 17 | 286.76 |
| hoc-bong-kkht | recursive | 6 | 820.0 |
| hoc-bong-kkht | **heading (của tôi)** | 9 | 547.56 |
| quy-che-dao-tao-2025 | fixed_size | 98 | 893.28 |
| quy-che-dao-tao-2025 | by_sentences | 243 | 321.08 |
| quy-che-dao-tao-2025 | recursive | 104 | 754.88 |
| quy-che-dao-tao-2025 | **heading (của tôi)** | 127 | 669.43 |

## 2. Benchmark — 5 câu hỏi của nhóm, top-3 mỗi chiến lược

### Câu 1: Sinh viên không thuộc diện cảnh báo học tập được đăng ký tối đa và tối thiểu bao nhiêu tín chỉ trong một học kỳ chính?

> Lưu ý: bẫy: đoạn gần giống ở chương thạc sĩ cũng có 24/12 TC

| Chiến lược | # | Score | doc_id | Chunk (rút gọn) | Hit |
|---|---:|---:|---|---|---|
| `fixed_size` | 1 | 0.745 | quy-che-dao-tao-2025 | tối đa 20 TC trong một học kỳ nhưng không vượt quá 30 TC trong một năm học. Học kỳ cuối kh… |  |
| `fixed_size` | 2 | 0.738 | quy-che-dao-tao-2025 | nh thức buộc những sinh viên đang bị cảnh báo học tập từ mức 2 trở lên đăng ký số TC học p… |  |
| `fixed_size` | 3 | 0.737 | quy-che-dao-tao-2025 | . Học kỳ hè không có đợt điều chỉnh đăng ký. 2. Số lượng TC đăng ký: a) Sinh viên không th… | ✅ |
| `by_sentences` | 1 | 0.783 | quy-che-dao-tao-2025 | Sinh viên được đăng ký tối đa 8 TC trong học kỳ hè. b) Sinh viên đang bị cảnh báo học tập … |  |
| `by_sentences` | 2 | 0.759 | quy-che-dao-tao-2025 | Quy định này không xét tới số TC của các học phần học cải thiện điểm. b) Sinh viên đã chịu… |  |
| `by_sentences` | 3 | 0.750 | quy-che-dao-tao-2025 | Sinh viên không tốt nghiệp được quyền đề nghị cấp chứng nhận với các học phần đã tích lũy … |  |
| `recursive` | 1 | 0.759 | quy-che-dao-tao-2025 | tập này không phụ thuộc vào điều kiện nâng mức cảnh báo học tập tại mục a và mục b khoản n… |  |
| `recursive` | 2 | 0.748 | quy-che-dao-tao-2025 | 4. Khối lượng tối đa được công nhận, chuyển đổi không vượt quá 50% khối lượng chương trình… |  |
| `recursive` | 3 | 0.738 | quy-che-dao-tao-2025 | 2. Hạng tốt nghiệp được xếp dựa trên điểm trung bình toàn khóa như xếp loại học lực quy đị… |  |
| `heading` | 1 | 0.799 | quy-che-dao-tao-2025 | Điều 10. Đăng ký học tập chương trình đại học — a) Sinh viên không thuộc diện cảnh báo học… | ✅ |
| `heading` | 2 | 0.774 | quy-che-dao-tao-2025 | Điều 19. Cảnh báo học tập và buộc thôi học — tập này không phụ thuộc vào điều kiện nâng mứ… |  |
| `heading` | 3 | 0.725 | quy-che-dao-tao-2025 | Điều 19. Cảnh báo học tập và buộc thôi học — 1. Kết quả học tập được đánh giá vào cuối mỗi… |  |

### Câu 2: Điều kiện để sinh viên được xét học bổng khuyến khích học tập loại A, B và C là gì?

| Chiến lược | # | Score | doc_id | Chunk (rút gọn) | Hit |
|---|---:|---:|---|---|---|
| `fixed_size` | 1 | 0.839 | hoc-bong-kkht | khóa, ngành đào tạo theo thứ tự ưu tiên từ loại A đến loại C cho đến khi hết quỹ học bổng.… |  |
| `fixed_size` | 2 | 0.745 | hoc-bong-kkht | 2020 của Hội đồng Trường. 2. Quy định này áp dụng đối với sinh viên hệ đại học của Trường … |  |
| `fixed_size` | 3 | 0.717 | hoc-bong-kkht | cả các học phần không tính điểm GPA) tại học kỳ cấp học bổng; g) Học quá thời gian thiết k… |  |
| `by_sentences` | 1 | 0.823 | hoc-bong-kkht | Khuyến khích và ưu tiên hình thức cấp kinh phí hỗ trợ (tương đương với mức học bổng) gắn v… |  |
| `by_sentences` | 2 | 0.776 | hoc-bong-kkht | Các quy định chung** 1. Học bổng khuyến khích học tập (KKHT) cấp cho các sinh viên được lự… |  |
| `by_sentences` | 3 | 0.775 | hoc-bong-kkht | Nguyên tắc xét cấp học bổng** 2 1. Sử dụng kết quả học tập và rèn luyện của học kỳ liền tr… |  |
| `recursive` | 1 | 0.818 | hoc-bong-kkht | 4. Khuyến khích và ưu tiên hình thức cấp kinh phí hỗ trợ (tương đương với mức học bổng) gắ… |  |
| `recursive` | 2 | 0.744 | hoc-bong-kkht | 2. Quy định này áp dụng đối với sinh viên hệ đại học của Trường ĐHBK Hà Nội. ## **Điều 2. … |  |
| `recursive` | 3 | 0.716 | hoc-bong-kkht | h) Học chương trình đào tạo do trường đối tác nước ngoài cấp một văn bằng tốt nghiệp duy n… |  |
| `heading` | 1 | 0.759 | hoc-bong-kkht | Điều 4. Nguyên tắc xét cấp học bổng — 2 1. Sử dụng kết quả học tập và rèn luyện của học kỳ… |  |
| `heading` | 2 | 0.747 | hoc-bong-kkht | Điều 2. Các quy định chung — 1. Học bổng khuyến khích học tập (KKHT) cấp cho các sinh viên… |  |
| `heading` | 3 | 0.713 | hoc-bong-kkht | Điều 4. Nguyên tắc xét cấp học bổng — c) Có học phần đạt điểm F tại học kỳ lấy điểm xét cấ… |  |

### Câu 3: Học phí chương trình đào tạo chuẩn năm học 2025-2026 được quy định như thế nào đối với các ngành Khoa học máy tính và Kỹ thuật hóa học?

> Lưu ý: gold answer nằm trong BẢNG ở Phụ lục I

| Chiến lược | # | Score | doc_id | Chunk (rút gọn) | Hit |
|---|---:|---:|---|---|---|
| `fixed_size` | 1 | 0.753 | hoc-phi-2025-2026 | m vừa học và sau đại học đối với năm học 2025-2026;_ _Theo đề nghị của ông Trưởng Ban Đào … |  |
| `fixed_size` | 2 | 0.717 | quy-che-dao-tao-2025 | độ tiến sĩ, ban hành theo Thông tư số 18/2021/TT-BGDĐT ngày 28 tháng 06 năm 2021 của Bộ tr… |  |
| `fixed_size` | 3 | 0.696 | quy-che-dao-tao-2025 | đại học;_ _Căn cứ Thông tư số 18/2021/TT-BGDĐT ngày 28 tháng 06 năm 2021 của Bộ Giáo dục v… |  |
| `by_sentences` | 1 | 0.727 | quy-che-dao-tao-2025 | Quy chế này được áp dụng từ học kỳ 1 năm học 2025-2026 cho tất cả các khóa đào tạo, trừ mộ… |  |
| `by_sentences` | 2 | 0.720 | quy-che-dao-tao-2025 | > 2 Quy chế tuyển sinh và đào tạo trình độ thạc sĩ, ban hành theo Thông tư số 23/2021/TT-B… |  |
| `by_sentences` | 3 | 0.698 | quy-che-dao-tao-2025 | Hiệu lực thi hành** 1. Quy chế này có hiệu lực thi hành từ học kỳ 1 năm học 2025-2026 và t… |  |
| `recursive` | 1 | 0.720 | quy-che-dao-tao-2025 | > 2 Quy chế tuyển sinh và đào tạo trình độ thạc sĩ, ban hành theo Thông tư số 23/2021/TT-B… |  |
| `recursive` | 2 | 0.710 | hoc-phi-2025-2026 | _Theo đề nghị của ông Trưởng Ban Đào tạo._ # **QUYẾT ĐỊNH:** **Điều 1.** Phê duyệt mức học… |  |
| `recursive` | 3 | 0.707 | quy-che-dao-tao-2025 | _Căn cứ Thông tư số 18/2021/TT-BGDĐT ngày 28 tháng 06 năm 2021 của Bộ Giáo dục và Đào tạo … |  |
| `heading` | 1 | 0.725 | quy-che-dao-tao-2025 | Điều 48. Hiệu lực thi hành — 1. Quy chế này có hiệu lực thi hành từ học kỳ 1 năm học 2025-… |  |
| `heading` | 2 | 0.723 | hoc-phi-2025-2026 | Phụ lục I MỨC HỌC PHÍ CÁC CHƯƠNG TRÌNH ĐÀO TẠO ĐẠI HỌC CHÍNH QUY, KỸ SƯ CHUYÊN SÂU, VỪA LÀ… |  |
| `heading` | 3 | 0.717 | hoc-phi-2025-2026 | Phụ lục I MỨC HỌC PHÍ CÁC CHƯƠNG TRÌNH ĐÀO TẠO ĐẠI HỌC CHÍNH QUY, KỸ SƯ CHUYÊN SÂU, VỪA LÀ… |  |

### Câu 4: Chứng chỉ tiếng Anh dùng để xét miễn học các học phần ngoại ngữ cơ bản phải đáp ứng những điều kiện gì?

> Lưu ý: gold answer trải trên Điều 3 VÀ Phụ lục II

| Chiến lược | # | Score | doc_id | Chunk (rút gọn) | Hit |
|---|---:|---:|---|---|---|
| `fixed_size` | 1 | 0.812 | quy-dinh-ngoai-ngu-k70 | , quốc tế; - Hoặc dựa trên điểm thi môn tiếng Anh của kỳ thi tốt nghiệp trung học phổ thôn… | ✅ |
| `fixed_size` | 2 | 0.692 | quy-dinh-ngoai-ngu-k70 | ** # **QUY ĐỊNH** **Phân loại trình độ đầu vào, chương trình ngoại ngữ cơ bản** **và chuẩn… | ✅ |
| `fixed_size` | 3 | 0.686 | quy-dinh-ngoai-ngu-k70 | uy từ khóa 70;_ _Theo đề nghị của Trưởng ban Ban Đào tạo._ ## **QUYẾT ĐỊNH:** **Điều 1.** … |  |
| `by_sentences` | 1 | 0.758 | quy-dinh-ngoai-ngu-k70 | ## **Điều 2. Phân loại trình độ đầu vào và phân lớp học ngoại ngữ cơ bản** 1. Căn cứ phân … | ✅ |
| `by_sentences` | 2 | 0.739 | quy-dinh-ngoai-ngu-k70 | Việc lựa chọn tiêu chí phân loại trong số các tiêu chí trên do Giám đốc Đại học Bách khoa … |  |
| `by_sentences` | 3 | 0.713 | quy-dinh-ngoai-ngu-k70 | Điều kiện xét quy đổi tương đương chứng chỉ và miễn học** - Kết quả bài kiểm tra TOEIC Pla… | ✅ |
| `recursive` | 1 | 0.733 | quy-dinh-ngoai-ngu-k70 | Việc lựa chọn tiêu chí phân loại trong số các tiêu chí trên do Giám đốc Đại học Bách khoa … |  |
| `recursive` | 2 | 0.726 | quy-che-dao-tao-2025 | 2. Đạt chuẩn ngoại ngữ đầu ra tương đương bậc 4/6 theo Khung năng lực ngoại ngữ 6 bậc dùng… |  |
| `recursive` | 3 | 0.725 | quy-dinh-ngoai-ngu-k70 | 2. Chứng chỉ tiếng Anh phải đánh giá đầy đủ 4 kỹ năng nghe, nói, đọc, viết; đồng thời phải… | ✅ |
| `heading` | 1 | 0.794 | quy-dinh-ngoai-ngu-k70 | Điều 2. Phân loại trình độ đầu vào và phân lớp học ngoại ngữ cơ bản — 1. Căn cứ phân loại … | ✅ |
| `heading` | 2 | 0.756 | quy-dinh-ngoai-ngu-k70 | Điều 4. Lộ trình học tập các học phần ngoại ngữ cơ bản — 4. Sinh viên không được phép hủy … | ✅ |
| `heading` | 3 | 0.722 | quy-dinh-ngoai-ngu-k70 | Điều 3. Công nhận, xét miễn học phần ngoại ngữ cơ bản — 1. Các học phần NNCB của các CTĐT … |  |

### Câu 5: Một học phần được coi là tương đương với học phần khác khi đáp ứng điều kiện nào về nội dung chuyên môn và số tín chỉ?

| Chiến lược | # | Score | doc_id | Chunk (rút gọn) | Hit |
|---|---:|---:|---|---|---|
| `fixed_size` | 1 | 0.774 | quy-che-dao-tao-2025 | ầu trong CTĐT, tuy nhiên cần đảm bảo số tín chỉ của học phần tương đương tối thiểu bằng ho… |  |
| `fixed_size` | 2 | 0.735 | quy-che-dao-tao-2025 | lượng giảng dạy trên lớp đối với lớp học phần rút gọn tối thiểu bằng 50% so với lớp học ph… |  |
| `fixed_size` | 3 | 0.701 | quy-che-dao-tao-2025 | hoàn thành đầy đủ các học phần theo yêu cầu của CTĐT trong thời gian quy định, bao gồm cả … |  |
| `by_sentences` | 1 | 0.737 | quy-che-dao-tao-2025 | Trong trường hợp cần thiết, người học được tùy chọn học một học phần tương đương để lấy kế… |  |
| `by_sentences` | 2 | 0.709 | quy-che-dao-tao-2025 | c) Nhóm học phần tự chọn: người học chọn lựa một số học phần trong danh mục để tích lũy đủ… | ✅ |
| `by_sentences` | 3 | 0.704 | quy-che-dao-tao-2025 | Kết thúc mỗi học kỳ, sinh viên tham gia khảo sát lấy ý kiến phản hồi về các điều kiện bảo … |  |
| `recursive` | 1 | 0.809 | quy-che-dao-tao-2025 | a) Hai học phần được coi là tương đương khi có nội dung chuyên môn trùng lặp tối thiểu 70%… | ✅ |
| `recursive` | 2 | 0.754 | quy-dinh-hanh-chinh | b) Xác nhận kết quả học tập của sinh viên; bao gồm kết quả học tập toàn khóa, kết quả học … |  |
| `recursive` | 3 | 0.726 | quy-che-dao-tao-2025 | a) Sinh viên đã học học phần đó ít nhất 02 lần nhưng chưa đạt; b) Điểm quá trình của học p… |  |
| `heading` | 1 | 0.821 | quy-che-dao-tao-2025 | Điều 4. Tín chỉ và học phần — a) Hai học phần được coi là tương đương khi có nội dung chuy… | ✅ |
| `heading` | 2 | 0.754 | quy-dinh-hanh-chinh | b) Xác nhận kết quả học tập của sinh viên; bao gồm kết quả học tập toàn khóa, kết quả học … |  |
| `heading` | 3 | 0.706 | quy-che-dao-tao-2025 | Điều 28. Học bổ sung, công nhận tín chỉ — b) Các học phần công nhận được xác định khi xét … |  |

### Bảng điểm tổng (tự động, theo docs/SCORING.md: top-1 đúng = 2đ, top-2/3 = 1đ)

| Chiến lược | Điểm /10 |
|---|---:|
| `heading` | 6 |
| `fixed_size` | 3 |
| `by_sentences` | 3 |
| `recursive` | 3 |

## 3. A/B metadata filter (chiến lược heading)

Câu hỏi: *Sinh viên nộp hồ sơ ở đâu và cần giấy tờ gì để được xác nhận kết quả học tập?*

**search() — không lọc**

| # | Score | doc_id | audience | Chunk (rút gọn) |
|---:|---:|---|---|---|
| 1 | 0.692 | quy-dinh-hanh-chinh | all | IL. Hướng dẫn thực hiện xác nhận văn bằng tốt nghiệp, chứng chỉ, kết q… |
| 2 | 0.688 | thu-tuc-chuyen-truong | student | 3. Các giấy tờ cần chuẩn bị Minh chứng xếp hạng của cơ sở giáo dục dại… |
| 3 | 0.632 | quy-che-dao-tao-2025 | student | Điều 35. Nghỉ học tạm thời và bảo lưu kết quả học tập — 5. Chế độ bảo … |

**search_with_filter(audience="student")**

| # | Score | doc_id | audience | Chunk (rút gọn) |
|---:|---:|---|---|---|
| 1 | 0.688 | thu-tuc-chuyen-truong | student | 3. Các giấy tờ cần chuẩn bị Minh chứng xếp hạng của cơ sở giáo dục dại… |
| 2 | 0.632 | quy-che-dao-tao-2025 | student | Điều 35. Nghỉ học tạm thời và bảo lưu kết quả học tập — 5. Chế độ bảo … |
| 3 | 0.629 | quy-che-dao-tao-2025 | student | Điều 28. Học bổ sung, công nhận tín chỉ — b) Các học phần công nhận đư… |

## 4. KnowledgeBaseAgent — kiểm tra grounding

```
[prompt 3014 ký tự, 3 chunk ngữ cảnh]
```

