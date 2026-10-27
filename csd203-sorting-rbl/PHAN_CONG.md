# Phân công và bằng chứng đóng góp

## Cập nhật tích hợp 28/10/2026

Đã nhận đủ gói My, Ngân, Hải, Thiện từ `src.zip`; giữ nguyên 97 file ở
`ban_giao/`, chép nguyên nội dung 27 file vào vị trí chung. Dân có thêm
Timsort/Powersort/noA, counted, test và tài liệu bàn giao. Chi tiết tại
[docs/TICH_HOP.md](docs/TICH_HOP.md), nguồn file ở
[ban_giao/README.md](ban_giao/README.md).

Quick/Merge/Heap/Radix đã thay các stub của bộ khung bằng source bàn giao.
Không chỉnh logic, không tự ghi đã được reviewer nghiệm thu. Bộ test
chung hiện đạt 72/72 trên CPython 3.12.13, không skip. Phần Dân có hỗ trợ
AI, cần thành viên tự đọc và review. Chưa có số liệu nghiên cứu chính
thức, commit/PR hoặc chữ ký review mới.

Các bảng “trạng thái ban đầu” bên dưới giữ lại làm lịch sử khởi tạo.
Nhật ký/phân công riêng của My và Ngân giữ nguyên trong `ban_giao/`.

| Thành viên | RQ | Triển khai | Review | Nhánh |
|---|---|---|---|---|
| My | RQ1 | Quick; kiểm tra generator D1–D3 | Merge/D4–D6; Heap | rq1-my |
| Ngân | RQ1 | Merge; kiểm tra generator D4–D6; tổng hợp paper | Quick/D1–D3; Radix | rq1-ngan |
| Hải | RQ2 | Heap; runner/worker/time; tích hợp và máy đo | Radix/mem/count; stack Powersort | rq2-hai |
| Thiện | RQ2 | Radix; mem/count/CSV; hình RQ2 | Heap/time/timeout; run/noA/stability | rq2-thien |
| Dân | RQ3 | Timsort/Powersort/noA; stability; ablation | Quick/Merge; đối chứng RQ3 | rq3-dan |

Hạ tầng ban đầu do AI tạo theo yêu cầu của Dân. Mỗi chủ module phải đọc, kiểm chứng, sửa và lưu bằng chứng; không ghi nhận đây là code do thành viên đã tự triển khai.

## Theo dõi bàn giao

| Thành phần | Trạng thái ban đầu | Người phụ trách | Điều kiện bàn giao |
|---|---|---|---|
| Quick/Merge/Heap/Radix | TODO, cờ False | Theo bảng trên | Đúng biến thể, test/fuzz/count đạt, reviewer xác nhận |
| Timsort và noA | TODO, cờ False | Dân | Đủ Power/minrun/run/buffer ngắn; stability và ablation đúng |
| Generator | Có bản tham chiếu | My, Ngân | Kiểm tra quy ước, test và input checksum |
| Runner/summary | Có bản khởi tạo chạy smoke | Hải, Thiện | Review ranh giới đo, trạng thái lỗi, CSV, môi trường |
| Biểu đồ | Có script timing cơ sở | Chủ RQ | Bổ sung bộ nhớ/count/RQ2/RQ3 từ CSV thật |
| Paper | Có outline | Cả nhóm, Ngân tổng hợp | Có số liệu thật, nguồn đã đọc, review |

## Nhật ký đóng góp

Thêm dòng sau mỗi phần việc; thay nội dung mẫu bằng bằng chứng thật.

| Ngày | Người | Module và thay đổi | Commit/PR | Reviewer | Test/CSV/bằng chứng |
|---|---|---|---|---|---|
| 2026-10-28 | Codex theo yêu cầu Dân | Gộp bốn gói, giữ nguyên source; thêm Timsort/noA và tài liệu phần Dân | Chưa commit | Chờ thành viên | 72 test đạt; SHA-256 97 bản gốc + 27 file tích hợp; xem docs/TICH_HOP.md |

D0 và hạn nộp: ghi theo lịch giảng viên. Chưa tự gán ngày lịch trong bộ khung.
