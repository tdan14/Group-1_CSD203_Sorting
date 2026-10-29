# Paper và slide

Paper cuối theo mẫu IEEE Conference hai cột, tối đa 6 trang nội dung; nộp PDF và nguồn Word/LaTeX. Tài liệu proposal không phải paper cuối.

- My: Quick, thời gian RQ1.
- Ngân: Merge, bộ nhớ RQ1; ghép bản thảo.
- Hải: Heap, Experimental Setup.
- Thiện: Radix, RQ2.
- Dân: Timsort/Powersort/noA, RQ3.
- Cả nhóm: Discussion, Threats, trích dẫn, khai báo AI, review và bảo vệ.

Dùng OUTLINE.md để chia nội dung, không đưa số liệu khi chưa chạy thật. Lưu slide vào slides/.

## Bản tổng hợp của Ngân

- `ieee/main.tex`: nguồn IEEE hai cột; `ieee/main.pdf`: bản đọc.
- `rq1_memory.md`: phân tích bộ nhớ RQ1, bảng median/min/max và giới hạn phép đo.
- `ieee/results_generated.tex` và `ieee/figures/`: tạo trực tiếp từ CSV đã audit.
- `python -B -m scripts.analyze_ngan` (chạy từ gốc dự án) tái tạo dữ liệu paper.

Phần viết được tổng hợp với hỗ trợ Codex; giữ ghi công từng chủ thuật toán.
`rq2_analysis.md` được tái tạo từ CSV đo mới, thay bảng cũ thiếu nguồn. Nhóm cần
review nội dung, xác nhận thông tin tác giả/lớp và tự chuẩn bị bảo vệ; không
coi bản PDF là xác nhận thay giảng viên hoặc chữ ký nghiệm thu của thành viên.
