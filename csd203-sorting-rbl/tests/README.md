# Kiểm thử sau tích hợp 28/10/2026

## Bổ sung phần Ngân — 30/10/2026

`test_quick` đối chiếu trình tự so sánh của đường thường/counted;
`test_radix` quan sát các truy cập mảng logic của đường thường, gồm khởi
tạo buffer và copy-back. Wrapper chỉ chạy trong test, không trong benchmark.
`test_ngan_analysis` kiểm tra audit bằng lượt worker nhỏ thật và các trường
hợp dữ liệu hỏng: thiếu/trùng, hash/oracle/count sai, môi trường sai,
source/raw CSV bị thay đổi và nhóm chưa đủ lượt thành công.

Chạy suite bằng lệnh bên dưới. Phần mô tả 72 test ngày 28/10 được giữ làm
lịch sử. `scripts.check_submissions` mặc định còn so sánh active file với
bản bàn giao cũ, nên báo các sửa đổi có chủ đích. Để xác minh riêng 97 bản
gốc, dùng `check_manifest('manifest.json', 'original')` từ module đó.
Audit dữ liệu paper: `python -B -m scripts.analyze_ngan --audit-only`.

Kết quả chạy lại trên CPython 3.12.14: **80/80 test đạt, không skip**.
`check_ready` đạt. Manifest cũ chỉ còn **96/97** khớp: bản
`ban_giao/thien/src/radix.py` đã được Thiện sửa tại commit `4faec1c`,
trước đợt này; tệp đó không có diff so với HEAD trong phiên Ngân.
Không sửa manifest để che thay đổi lịch sử.

## Kết quả tích hợp ban đầu

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
