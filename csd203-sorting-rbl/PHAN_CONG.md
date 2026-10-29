# Phân công và bằng chứng đóng góp

## Cập nhật phần Ngân — 30/10/2026

Ngân yêu cầu Codex hoàn thiện phần Merge, bộ nhớ RQ1, review Quick/Radix
và tổng hợp bài LaTeX bằng dữ liệu thực chạy. Các thuật toán, generator,
runner và config giữ nguyên tại `c73bc10`. Test mới quan sát trình tự so
sánh Quick và truy cập mảng logic Radix; không đo hiệu năng trên wrapper.

Bằng chứng được lưu ở `results/raw/ngan_20261029.csv`, manifest môi trường,
summary cùng tên và `paper/ieee/`. `scripts/analyze_ngan.py` kiểm tra ma
trận, tái sinh đầu vào, đối chiếu hash/checksum trước khi tạo bảng/hình.
Đây là máy phát triển của Ngân, không nhận là máy chính của Hải. Kết quả
trái giả thuyết được giữ lại. Các ghi nhận ngày 28–29/10 bên dưới là lịch sử;
review tự động có hỗ trợ AI không thay chữ ký review của My hoặc cả nhóm.

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
| 2026-10-29 | Thiện (`rq2-thien`) | Đồng nhất biến `pos` trong `src/radix.py` (loại bỏ 4N lượt đọc mảng theo góp ý Ngân); nộp methods_radix.md, rq2_hypothesis.md, rq2_analysis.md; review Heap của Hải và Timsort của Dân | `rq2-thien` | Ngân, Hải | 72/72 test PASS; test_radix PASS 1.000 fuzz cases; BAO_CAO_PHAN_HOI_THIEN.md |

D0 và hạn nộp: ghi theo lịch giảng viên. Chưa tự gán ngày lịch trong bộ khung.

Kiểm chứng phần Ngân: 80/80 test đạt trên CPython 3.12.14; check_ready đạt.
Ma trận mới có 1.308 lượt, tất cả status=ok. Manifest bàn giao lịch sử
khớp 96/97: bản Radix trong ban_giao/thien đã được sửa ở 4faec1c trước
đợt này; không phải sửa đổi mới của Ngân.
