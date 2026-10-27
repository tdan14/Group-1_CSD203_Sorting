# Phân công và bằng chứng đóng góp

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

D0 và hạn nộp: ghi theo lịch giảng viên. Chưa tự gán ngày lịch trong bộ khung.
