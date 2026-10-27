# Kiểm thử sau tích hợp 28/10/2026

Chạy tại `csd203-sorting-rbl/`:

```bash
python -B -X utf8 -m unittest discover -s tests -t . -v
python -B -m scripts.check_submissions
```

Bộ hiện tại có 72 test method, không skip. Năm file `test_generate`,
`test_quick`, `test_merge`, `test_heap`, `test_radix` giữ nguyên từ gói
Ngân. `test_timsort` kiểm tra phần mới của Dân. Test khung cũ được nối
với tên hàm generator và API runner/worker đã bàn giao. Không discover
các gói lịch sử trong `ban_giao/` như một suite chung.

Test kiểm tra tính đúng và tính ổn định không thay review cơ chế của
thành viên. Không đo timing trên comparator wrapper có bộ đếm. Trước
nghiệm thu, kiểm tra thêm `python -m scripts.check_ready` và các điểm
còn mở trong `docs/TICH_HOP.md`.
