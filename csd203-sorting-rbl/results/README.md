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

## Đợt đo Ngân ngày 29–30/10/2026

`raw/ngan_20261029.csv` là dữ liệu thực thi tuần tự trên máy phát triển,
không phải CSV mẫu. `environment_ngan_20261029.json` ghi môi trường thực tế,
commit đầy đủ và SHA-256 từng tệp source/config dùng đo. `run_id=run_main`
được giữ theo cấu hình gốc, không mang nghĩa đây là máy chính của Hải.

`summary/ngan_20261029.csv` được tạo sau khi `scripts.analyze_ngan` kiểm tra
ma trận, seed, môi trường, hash đầu vào và oracle checksum tái sinh độc lập.
Chỉ dòng status=ok được tổng hợp; n_ok và complete biểu thị đủ ba seed.
Các hình dùng trong paper nằm ở `paper/ieee/figures/`, tránh xuất thêm bản trùng.

Toàn CSV chỉ có một source/máy/Python/generator. Bản ghi thô không được sửa
để hợp giả thuyết. Mọi kết luận chỉ áp dụng cấu hình đã đo; bộ nhớ là cấp phát
bổ sung qua tracemalloc, không phải RSS. Trình audit xác nhận nhất quán và
khả năng truy vết, không chứng minh thuật toán đúng cho mọi đầu vào.
