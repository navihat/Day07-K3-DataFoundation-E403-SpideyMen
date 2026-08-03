# Dự đoán độ tương tự cosine — Trương Văn Thái

Backend: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|---|---|---|---|---:|---|
| 1 | Sinh viên được đăng ký tối đa bao nhiêu tín chỉ trong một học kỳ? | Số tín chỉ tối đa mà sinh viên được phép đăng ký trong học kỳ chính | cao | **0.787** | ✅ |
| 2 | Thời hạn nộp học phí của sinh viên là khi nào? | Điều kiện xét cấp học bổng khuyến khích học tập loại A | thấp | **0.388** | ✅ |
| 3 | Sinh viên được đăng ký tối đa 24 TC trong học kỳ chính. | Học viên được đăng ký tối đa 24 TC trong một học kỳ chính. | cao | **0.998** | ✅ |
| 4 | Sinh viên đăng ký tối đa 24 tín chỉ trong học kỳ chính. | Sinh viên đăng ký tối đa 24 TC trong học kỳ chính. | cao | **0.829** | ✅ |
| 5 | Chuẩn ngoại ngữ đầu ra đối với sinh viên K70 | Quy định về chứng chỉ tiếng Anh để xét miễn học phần ngoại ngữ | cao | **0.566** | ❌ |

**Lý do chọn từng cặp:**

1. cùng ý, chỉ khác cách diễn đạt — phép thử cơ bản nhất
2. khác chủ đề hoàn toàn, dù cùng miền văn bản quy định đại học
3. BẪY (§5.4b): chỉ khác đúng một từ chỉ đối tượng, nhưng khác nhau về pháp lý
4. §5.4a: cùng nghĩa, chỉ khác viết tắt — nếu điểm THẤP thì câu 1 sẽ khó truy xuất
5. liên quan nhưng không đồng nghĩa — kỳ vọng thấp hơn cặp 1
