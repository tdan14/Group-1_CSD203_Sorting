# Quy ước triển khai

> Cập nhật 28/10/2026: đã tích hợp source bàn giao. Lệnh chạy hiện tại
> dùng `--config`, `--algo`, `--mode` của Hải, xem [README](../README.md).
> Các quy ước/lệnh từ bộ khung dưới đây là tài liệu ban đầu; trạng thái
> khác biệt được ghi tại [TICH_HOP.md](TICH_HOP.md).

- CPython 3.12; đồng bộ đầy đủ patch version với máy Hải. Core Python thuần, GC bật, không setrecursionlimit.
- `sort(a) -> None` thay đổi a; không bộ đếm, log, I/O, oracle hoặc kiểm tra miền trong vùng đo.
- `sort_counted(a) -> dict` cùng quyết định thuật toán; đủ key trong src/contracts.py. None cho trường không áp dụng. Radix đếm đọc/ghi mảng, thuật toán còn lại đếm so sánh khóa thực tế.
- Merge/Timsort hỗ trợ __lt__ theo key; test order riêng; không dùng tuple ordering cả key/order làm bằng chứng stability.
- Timsort: lấy run ngắn hơn làm buffer khi gộp; chỉ đảo run giảm ngặt để giữ ổn định. minrun, Power và merge policy phải ánh xạ tới tài liệu gốc.
- noA chỉ tắt nhận diện run, chia khối minrun; không đổi chính sách gộp hoặc buffer. Không Galloping/noB.
- SHA-256 đầu vào: số unsigned 32-bit little-endian theo thứ tự. output_check: h=(31*h+x) mod 2**64, bắt đầu 0. So sánh đầy đủ oracle ngoài vùng đo; checksum không thay oracle.
- Worker riêng cho time/mem/count. `--mem`, `--count` là alias CLI. Bộ nhớ đo cấp phát thêm sau khi đã có input/bản sao; không phải tổng RAM/RSS của tiến trình.
- Mỗi lượt timeout 60 giây toàn subprocess; stderr phát phase. Timeout ở generate/validate không chứng minh riêng thuật toán cần >60 giây.
- CSV dùng UTF-8, số thập phân dấu chấm. Timeout/crash/oom/wrong để trống số đo hiệu năng. Không gán timeout thành đúng 60 giây.
- Một cấu hình gồm 3 seed 2026/2027/2028, không phải 3 lượt cho mỗi seed. Báo median/min/max, số lượt ok, giữ lỗi.
- Speedup = median baseline / median phương án trên cùng mode/dữ liệu/máy/code. Giảm do run = (T_noA-T_timsort)/T_noA*100%; chấp nhận giá trị âm.
- `lib-sorted` là baseline thư viện C, count không áp dụng. Không quy chênh lệch tốc độ Python/C hoàn toàn cho một cơ chế thuật toán.
- Test timeout/wrong/crash của harness dùng mock chỉ trong tests; không sinh hàng dữ liệu giả trong results/raw.

## Ma trận

Xem bench/configs.json. `python -m bench.runner --official --dry-run` xuất toàn bộ công việc sau gộp cấu hình trùng, không thực thi. `rq` có thể là RQ1;RQ2;RQ3 để dùng lại kết quả chung. Lượt mới ở run_id khác giữ riêng khi summary.

## Môi trường

Chạy capture_environment trên máy đo, điền CPU/RAM/chế độ nguồn còn thiếu và commit. RAM dùng byte. Đổi máy hoặc generator phải lưu phiên bản và không gộp số liệu cũ như cùng điều kiện.

## Phần hạ tầng cần nhóm review thêm

- Đối chiếu cài đặt runner với đặc tả giảng viên, đo overhead thực tế và kiểm tra giới hạn tài nguyên trên máy Hải.
- Kiểm tra đường chạy counted không lệch nhánh/so sánh so với timing.
- Script plot hiện chỉ vẽ timing. Chủ RQ bổ sung hình bộ nhớ, operation, sensitivity và ablation; không chỉ dựa một hình tăng trưởng.
