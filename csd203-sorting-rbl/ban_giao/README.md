# Các gói bàn giao gốc

Lấy từ `src.zip` do người dùng cung cấp ngày 28/10/2026. Nội dung file được
chép nguyên byte; không chỉnh sửa logic, định dạng hoặc lời ghi của tác giả.

| Thư mục | Gói trong ZIP | Nội dung đáng chú ý |
|---|---|---|
| `my/` | `src My/` | Quick, generator D1–D3 cũ, test, bàn giao My → Ngân, tài liệu ôn tập, bản thảo, script/hình/CSV mẫu RQ1 |
| `ngan/` | `src Ngan/` | Merge, test review, methods Merge, phân công và AI log cập nhật |
| `hai/` | `src Hai/` | Heap, runner/worker, ma trận, generator chung, biểu đồ, báo cáo sửa đổi |
| `thien/` | `src Thien/` | Radix, bản worker/runner trước bàn giao, hướng dẫn Thiện → Hải, môi trường và test |

Giữ 97 file, kể cả file rỗng phục vụ cấu trúc thư mục. Chỉ bỏ metadata
`.git/`, cache `__pycache__/` và `.pyc` khi đưa vào repo chung. ZIP gốc
không bị thay đổi. File `.gitignore` bổ sung trong `my/results/` giúp Git
nhận hai hình bàn giao dù `.gitignore` gốc của My bỏ qua thư mục hình.

`manifest.json` ghi đường dẫn nguồn và SHA-256 của 97 file gốc.
`integrated.json` ghi nguồn và SHA-256 của 27 file được chép vào vị trí
chạy chung. Từ thư mục dự án, kiểm tra bằng:

```bash
python -m scripts.check_submissions
```

Các gói có file trùng tên hoặc khác phiên bản. Bản lưu ở đây giúp giữ đủ
lịch sử; chỉ `src/`, `data/`, `bench/`, `tests/` ở thư mục dự án được dùng
khi chạy theo README. Không chạy discover đệ quy từ `ban_giao/`: các test
cũ được viết cho trạng thái riêng của từng gói, như D4–D6 còn là stub
trong gói My.

`my/bench/sample_rq1_data.csv` và hai hình ở `my/results/figures/` là dữ
liệu/hình minh họa được bàn giao, không được đưa vào kết quả nghiên cứu
như số liệu đo thật.
