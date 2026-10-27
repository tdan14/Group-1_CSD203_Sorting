# RQ3 — giả thuyết và kế hoạch phân tích

So sánh `quick`, `merge`, `timsort`, `timsort-noA`, `lib-sorted` trên cùng
đầu vào. Dùng N=100.000 và 1.000.000; D1–D4, D5 với K=1000/10/2, D6 với
R=2/16/256; seed 2026/2027/2028. Ma trận đã có trong `bench/configs.json`.

Giả thuyết trước đo: nhận diện run có thể giúp Timsort giảm công việc trên
D2, D4 và các lô D6 dài. Với D1, chi phí dò run có thể làm lợi ích nhỏ
hơn. Dữ liệu trùng khóa còn ảnh hưởng độ dài run; cần xem kết quả D5 thay
vì suy đoán từ tên thuật toán. Đây đều là giả thuyết, chưa phải kết quả.

Chạy time, mem và count riêng. `lib-sorted` chỉ đo time/mem. Chỉ tổng hợp
dòng `ok`, giữ số lượt lỗi và số lượt thành công. Không gộp khác máy,
commit, phiên bản Python hoặc generator như cùng một điều kiện.

- Báo median, min, max và n_ok cho từng cấu hình.
- Speedup của phương án so với baseline = T_baseline / T_phương_án.
- Mức giảm thời gian nhờ nhận diện run =
  (T_noA − T_timsort) / T_noA × 100%; giữ cả kết quả âm.
- Xem đồng thời thời gian, đỉnh bộ nhớ và số so sánh khóa.

Mỗi biểu đồ phải truy được về CSV thật. `bench.plot --csv ... --rq RQ3`
đã có phần hình/bảng RQ3 từ Hải. CSV mẫu trong gói My chỉ dùng minh họa,
không dùng cho kết luận. Khoảng cách với `lib-sorted` còn chịu khác biệt
Python/C và các cơ chế thư viện; không quy toàn bộ cho Powersort.

Ngân nhận Methods Timsort và nội dung RQ3 này để ghép paper khi có số
liệu chính thức. Dân kiểm tra các kết quả trái giả thuyết và viết hạn chế.
