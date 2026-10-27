# Kiểm tra bộ khung trước bàn giao

Môi trường kiểm tra đóng gói: Linux, CPython 3.12.14. Chưa kiểm tra trực tiếp trên Windows; README dùng lệnh gọi Python venv để tránh phụ thuộc PowerShell activation.

- unittest: 26 test; 11 đạt, 15 SKIP do các module thuật toán nghiên cứu chưa được nhóm triển khai.
- Chạy runner lib-sorted trên D1/time và D6/mem: status ok, có manifest và CSV thật ở khu vực smoke thử nghiệm.
- Kiểm tra timeout không ghi thời gian hoàn thành; lỗi wrong/oom/crash không được dùng tính tốc độ.
- Summary smoke tạo được median/min/max; không đánh dấu đủ 3 seed chính thức.
- Script plot chạy được trên summary smoke khi cho phép preview chưa hoàn chỉnh.
- Ma trận chính thức sau gộp cấu hình trùng: 1.308 lượt worker. Đây là kế hoạch, không phải kết quả đã đo.
- Kiểm tra guard: check_ready exit 1; chạy thuật toán TODO hoặc benchmark chính thức exit 2. Đây là hành vi đúng ở thời điểm bàn giao.
- requirement.txt tham chiếu requirements.txt và cài được khi không có mạng; core không cần thư viện ngoài.
- ZIP được giải nén vào thư mục mới để chạy lại test và một cấu hình lib-sorted.

Các CSV/hình smoke dùng kiểm tra đóng gói không được đưa vào ZIP. Nhóm tự tạo run mới trên máy của mình; không coi kiểm tra hạ tầng này là nghiệm thu thuật toán hoặc nghiên cứu.
