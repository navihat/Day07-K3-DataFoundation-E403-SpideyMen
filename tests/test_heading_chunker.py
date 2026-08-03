"""Test cho HeadingChunker — chiến lược riêng của Giai đoạn 2.

File tách riêng khỏi `test_solution.py` (bộ 42 test được chấm của Giai đoạn 1).

    pytest tests/test_heading_chunker.py -v
"""

import unittest

from src.src_thai_01801 import HeadingChunker

QUY_CHE = """
Chương II ĐÀO TẠO ĐẠI HỌC

Điều 10. Đăng ký học tập chương trình đại học

1. Đăng ký học tập là quy trình bắt buộc của sinh viên cho mỗi học kỳ.
2. Số lượng TC đăng ký: sinh viên không thuộc diện cảnh báo học tập được đăng ký
tối đa 24 TC và tối thiểu 12 TC trong học kỳ chính.

Điều 11. Công nhận kết quả học tập và chuyển đổi tín chỉ

Sinh viên được công nhận kết quả học tập của học phần đã tích lũy tại cơ sở đào tạo khác.

Chương IV ĐÀO TẠO THẠC SĨ

Điều 30. Đăng ký học tập chương trình thạc sĩ

Học viên có thể đăng ký tối thiểu 12 TC và tối đa 24 TC trong một học kỳ chính.
"""


class TestHeadingChunker(unittest.TestCase):

    def test_returns_list_of_strings(self):
        chunks = HeadingChunker().chunk(QUY_CHE)
        self.assertIsInstance(chunks, list)
        for chunk in chunks:
            self.assertIsInstance(chunk, str)

    def test_empty_text_returns_empty_list(self):
        self.assertEqual(HeadingChunker().chunk(""), [])
        self.assertEqual(HeadingChunker().chunk("   \n  "), [])

    def test_splits_on_dieu_boundary(self):
        chunks = HeadingChunker(min_chunk_size=1).chunk(QUY_CHE)
        # mỗi Điều nằm ở một chunk khác nhau
        dieu_10 = [c for c in chunks if "Điều 10" in c]
        dieu_11 = [c for c in chunks if "Điều 11" in c]
        self.assertTrue(dieu_10 and dieu_11)
        self.assertNotEqual(dieu_10[0], dieu_11[0])

    def test_heading_is_kept_inside_chunk(self):
        """Điểm cốt lõi của chiến lược: chunk phải tự khai báo nó thuộc Điều nào."""
        chunks = HeadingChunker(min_chunk_size=1).chunk(QUY_CHE)
        chunk_24tc = next(c for c in chunks if "tối đa 24 TC và tối thiểu 12 TC" in c)
        self.assertIn("Điều 10", chunk_24tc)
        self.assertIn("chương trình đại học", chunk_24tc)

    def test_near_duplicate_passages_are_distinguishable(self):
        """Đoạn 24/12 TC của đại học và của thạc sĩ phải phân biệt được (§5.4b)."""
        chunks = HeadingChunker(min_chunk_size=1).chunk(QUY_CHE)
        dai_hoc = next(c for c in chunks if "Điều 10" in c)
        thac_si = next(c for c in chunks if "Điều 30" in c)
        self.assertIn("đại học", dai_hoc)
        self.assertIn("thạc sĩ", thac_si)
        self.assertNotEqual(dai_hoc, thac_si)

    def test_long_section_is_split_but_keeps_heading(self):
        long_text = "Điều 5. Học phí\n\n" + ("Sinh viên nộp học phí đúng hạn. " * 200)
        chunks = HeadingChunker(max_chunk_size=400).chunk(long_text)
        self.assertGreater(len(chunks), 1)
        for chunk in chunks:
            self.assertIn("Điều 5", chunk)

    def test_short_sections_are_merged(self):
        text = "Điều 1. A\n\nNgắn.\n\nĐiều 2. B\n\nCũng ngắn.\n\nĐiều 3. C\n\nRất ngắn."
        merged = HeadingChunker(min_chunk_size=200).chunk(text)
        separate = HeadingChunker(min_chunk_size=1).chunk(text)
        self.assertLess(len(merged), len(separate))

    def test_falls_back_when_no_heading(self):
        plain = "Văn bản không có tiêu đề nào cả. " * 50
        chunks = HeadingChunker(max_chunk_size=200).chunk(plain)
        self.assertGreater(len(chunks), 1)

    def test_recognises_phu_luc(self):
        text = "Điều 1. Mở đầu\n\nNội dung điều một.\n\nPhụ lục II Bảng quy đổi\n\nIELTS 6.0 tương đương B2."
        chunks = HeadingChunker(min_chunk_size=1).chunk(text)
        self.assertTrue(any("Phụ lục II" in c for c in chunks))

    def test_markdown_heading_noise_is_stripped(self):
        text = "## **Điều 7. Đánh giá**\n\nNội dung điều bảy dài hơn ngưỡng tối thiểu một chút."
        chunk = HeadingChunker(min_chunk_size=1).chunk(text)[0]
        self.assertNotIn("#", chunk)
        self.assertNotIn("**", chunk)
        self.assertTrue(chunk.startswith("Điều 7"))


if __name__ == "__main__":
    unittest.main()
