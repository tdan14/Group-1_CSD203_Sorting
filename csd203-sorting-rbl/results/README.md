# Kết quả

Chưa chạy ma trận nghiên cứu chính thức trong lần tích hợp 28/10/2026.

- `raw/`: CSV đo thật, runner ghi vào đường dẫn truyền qua `--out`.
- `smoke/`: CSV kiểm tra hạ tầng, đã gitignore, không dùng kết luận paper.
- `figures/`: hình và bảng tổng hợp từ `bench.plot --csv ... --rq ...`.
- `summary/`: chỗ lưu tổng hợp riêng nếu nhóm dùng công cụ bổ sung.

Không sửa/ghi đè CSV gốc; dùng file mới cho mỗi đợt và đặt run_id qua
cấu hình. Runner Hải không tạo manifest riêng cho mỗi lần chạy; các cột
trong CSV chứa commit, máy, phiên bản generator/Python và checksum.
Nộp CSV cùng code/môi trường tương ứng. Không đưa dữ liệu lớn tái tạo
được vào Git. Không vẽ timeout như thời gian hoàn thành chính xác.

CSV mẫu và hai hình của My được giữ nguyên trong `ban_giao/my/`; đó là
minh họa bàn giao, không phải dữ liệu nghiên cứu chính thức.
