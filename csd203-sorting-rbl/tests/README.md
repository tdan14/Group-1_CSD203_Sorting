# Kiểm thử

Chạy `python -m unittest discover -s tests -v` từ repo root.

- Test generator và harness chạy ngay với thư viện chuẩn.
- Module thuật toán chưa hoàn thành được SKIP có tên; không coi kết quả này là nghiệm thu cả đề tài.
- Sau khi triển khai, đặt cờ READY/COUNTED_READY tương ứng. Test tự kích hoạt 1.000 ca fuzz và test count/stability.
- `python -m scripts.check_ready` phải exit 0 trước nghiệm thu. Tiếp tục kiểm tra test không còn SKIP và review cơ chế; cờ không chứng minh thuật toán đúng đặc tả.
- Dân bổ sung test riêng cho minrun 31/32/33/63/64/65, đảo run giảm ngặt, các khóa bằng nhau tại ranh giới, chỉ số Power và stack merge. Hải/Thiện review độc lập.
- Hàm đếm phải cùng quyết định thuật toán với bản timing. Không đo timing trên comparator wrapper có bộ đếm.
