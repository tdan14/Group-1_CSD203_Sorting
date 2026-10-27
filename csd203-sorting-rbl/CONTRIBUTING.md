# Cộng tác

1. Hải đưa bộ khung lên main và chia quyền repo cho cả nhóm.
2. Mỗi người clone repo và tạo nhánh theo PHAN_CONG.md. Không gửi lại ZIP cho nhau để ghép code.
3. Trước phiên làm việc: cập nhật main rồi merge main vào nhánh cá nhân. Nếu có conflict ở hợp đồng/module chung, trao đổi với Hải trước khi đổi giao diện.
4. Mỗi thay đổi gồm code + test + cập nhật phần liên quan. Commit mô tả việc thực hiện, không chỉ ghi "update".
5. Push nhánh và mở Pull Request vào main; ghi thuật toán/cơ chế, cách test, kết quả và người review theo PHAN_CONG.md.
6. Reviewer đọc code, chạy test và kiểm tra đặc tả. Hải ghép sau review. Cập nhật PHAN_CONG.md và AI_LOG.md nếu có sử dụng AI.
7. Benchmark chính thức chỉ chạy trên main đã commit sạch và môi trường ghi nhận. Mỗi run có thư mục mới; không sửa CSV gốc.

Ví dụ tạo nhánh của My sau khi clone:

```bash
git switch main
git pull --ff-only
git switch -c rq1-my
```

Cập nhật nhánh đang làm:

```bash
git fetch origin
git merge origin/main
```

Không cần cấu hình branch protection để chạy local. Hải nên yêu cầu ít nhất một review cho PR khi thiết lập repo; không tự gán username GitHub khi chưa biết tài khoản.
