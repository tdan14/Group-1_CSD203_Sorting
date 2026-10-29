# Ghi nhận tích hợp ngày 28/10/2026

Theo yêu cầu của Dân: ghép bài bốn thành viên và bổ sung phần Dân trước;
chưa cải thiện hoặc sửa logic của bốn thành viên.

## Nguồn các file đang chạy

| Vị trí chung | Nguồn giữ nguyên nội dung |
|---|---|
| `src/quick.py` | Gói Ngân; trùng bản Quick trong gói My |
| `src/merge.py` | Gói Ngân |
| `src/heap.py` | Gói Ngân; trùng gói Hải |
| `src/radix.py` | Gói Ngân; trùng gói Thiện/Hải |
| `data/generate.py` | Gói Ngân; trùng generator 1.1.0 của Hải |
| `bench/runner.py`, `worker.py`, `plot.py`, `configs.json`, `make_configs.py`, `env_info.py` | Gói Hải; cũng có trong gói Ngân |
| `tests/test_generate.py`, `test_quick.py`, `test_merge.py`, `test_heap.py`, `test_radix.py` | Gói Ngân, gồm test đã có và phần review bổ sung |
| `bench/plot_rq1.py`, ba bản thảo Quick/RQ1, ôn tập My | Gói My |
| `paper/methods_merge.md` | Gói Ngân |
| Hướng dẫn Thiện → Hải, báo cáo Hải, bàn giao My → Ngân | Chép nguyên file tương ứng vào gốc dự án |

Toàn bộ phần riêng còn lại, kể cả README/PHAN_CONG/AI_LOG khác phiên bản,
được giữ trong [ban_giao/](../ban_giao/README.md). Có manifest để kiểm tra
cả bản gốc lẫn 27 file được ghép vào vị trí chung. Không chạy formatter
hoặc đổi tên hàm bên trong các file này.

`.gitattributes` tắt chuyển đổi xuống dòng cho bản gốc và các file được
chép nguyên nội dung, giúp giữ SHA-256 sau khi Git checkout trên Windows.

## Phần nối từ bộ khung

- `src/registry.py` nhận giao diện hàm của các module bàn giao; không buộc
  My, Ngân, Hải, Thiện phải thêm cờ READY vào source.
- `bench/plan.py` đọc danh sách cấu hình của Hải, nhận các RQ nối bằng `+`.
- Test generator/harness của bộ khung đổi sang tên hàm/API đang bàn giao.
  Không chỉnh năm file test lấy từ gói Ngân.
- README và các ghi chú chung dùng lệnh runner của Hải.

`src/timsort.py`, `tests/test_timsort.py`, bàn giao/ôn tập/bản thảo Dân là
phần viết mới, có khai báo hỗ trợ AI trong `AI_LOG.md`.

## Kết quả kiểm tra

Trên CPython 3.12.13, Windows, máy phát triển:

```bash
python -B -X utf8 -m unittest discover -s tests -t . -v
python -B -X utf8 -m scripts.check_ready
python -B -m scripts.check_submissions
python -m bench.runner --config bench/configs.json --rq RQ3 --dry-run
```

Bộ test: **72/72 đạt, không skip**. Test gồm bộ bàn giao Ngân, test khung
đã nối lại API và 8 test riêng Timsort/noA. Mỗi thuật toán có fuzz; riêng
Dân kiểm tra cả bốn hàm trên 1.000 ca D1–D6, độ dài 0–200, cùng các ca
biên, ổn định 1.000 bản ghi, trình tự so sánh và policy Powersort.

Kiểm tra qua `bench.runner.run_single_trial`: Timsort và noA, mỗi bản 10
cấu hình D1–D6 × 3 chế độ, N=1001, seed=2026: **60/60 lượt ok**, oracle
đúng, SHA-256 đầu vào và output_check khớp giữa time/mem/count. Lệnh
`check_ready` trả 0; `--rq RQ3 --dry-run` chọn **840 lượt**, không chạy đo.
Đây là kiểm tra tích hợp, không lưu CSV nghiên cứu hay kết luận tốc độ.

## Những điểm giữ nguyên để nhóm review sau

- Ngân đã nêu chênh lệch bộ đếm đọc Radix: đường thường đọc nhiều hơn
  đường counted 4N lần với N >= 2. Thiện đã xử lý xong vào ngày 29/10/2026
  bằng cách đồng nhất dùng biến `pos = count[byte_val] - 1` trên cả hai
  đường chạy `sort(a)` và `sort_counted(a)`, loại bỏ hoàn toàn 4N lần đọc thừa.
  Đã kiểm chứng lại 72/72 test đạt trên CPython 3.12.
- `--resume` của runner dùng khóa theo commit/máy/cấu hình, chưa có
  run_id, generator_version hoặc python_version trong khóa; các trạng
  thái lỗi cũng được xem là đã có dòng. Dùng CSV mới cho đợt mới.
- Worker hiện vẫn có thể ghi elapsed_ms khi status=`wrong`. Giữ nguyên
  source; chỉ dùng dòng `ok` khi tổng hợp hiệu năng.
- My và Hải khai báo Matplotlib khác phiên bản. Bản gốc giữ đủ, chưa
  ép thống nhất dependency vẽ hoặc chạy lại các hình mẫu.
- Tài liệu bàn giao phản ánh thời điểm riêng, có chỗ còn nói thiếu Merge
  hoặc Timsort. Đọc chúng như lịch sử, đối chiếu trạng thái hiện tại ở đây.

Tại thời điểm tích hợp 28/10: chưa chạy ma trận nghiên cứu chính thức, chưa có paper hoàn chỉnh, chưa
có chữ ký review của thành viên. Không tự ghi nhóm đã nghiệm thu hoặc
đã tự viết phần được AI hỗ trợ. Thay đổi đang ở working tree, chưa commit
hay push.

Cập nhật 30/10: phần Ngân có dữ liệu đo trên máy phát triển, audit và bài
LaTeX tại `paper/ieee/`; xem mục mới trong `README.md`, `PHAN_CONG.md` và
`AI_LOG.md`. Các kết quả 72 test ở trên thuộc lần tích hợp trước. Không
đổi manifest bàn giao gốc để che các sửa đổi sau bàn giao.
