# Bàn giao phần Dân

Ngày 28/10/2026. Phần này do Codex hỗ trợ viết theo yêu cầu Dân. Dân cần
đọc, chạy thử và tự giải thích trước khi ghi nhận review hoặc bảo vệ.

## Các file

- `src/timsort.py`: Timsort/Powersort và noA, có bản thường và counted.
- `tests/test_timsort.py`: 8 test method riêng cho phần Dân.
- `paper/methods_timsort.md`: phần phương pháp để Ngân ghép paper.
- `paper/rq3_hypothesis.md`: giả thuyết và cách phân tích ablation RQ3.
- `docs/ON_TAP_VAN_DAP_DAN.md`: giải thích hàm và ví dụ để tự trace.

## Cách hoạt động

1. Tính minrun. Khi N < 64 thì minrun=N, với N lớn thì từ 32 đến 64.
2. Bản thường nhận diện run không giảm hoặc giảm nghiêm ngặt. Run giảm
   được đảo tại chỗ. Không đảo đoạn có khóa bằng nhau.
3. Run ngắn được kéo dài bằng Binary Insertion Sort. Khi khóa bằng nhau,
   chèn sau phần tử đã có để giữ ổn định.
4. Powersort tính power từ trung điểm hai run kề nhau; khi gặp ranh giới
   có power nhỏ hơn, gộp các ranh giới sâu hơn trong stack trước.
5. Khi gộp, chép run ngắn hơn làm buffer. Gộp từ đầu thì ưu tiên trái khi
   bằng nhau; gộp từ cuối thì ưu tiên phải khi bằng nhau.
6. noA bỏ nhận diện run, sắp từng khối minrun. Minrun, Binary Insertion,
   Powersort và merge còn lại được giữ chung. Không có Galloping/noB.

Code dùng hàm thường, `if`, `for`, `while` tách dòng; không lambda,
comprehension hoặc vòng lặp gộp một dòng. Đường thường không cập nhật
bộ đếm. Đường counted viết tường minh các phép so sánh; test xác nhận
trình tự so sánh giống đường thường.

## Chỉ số counted

`key_comparisons` đếm mỗi lần so sánh khóa trong nhận diện run, Binary
Insertion và merge. `array_reads`/`array_writes` để `None`; phần này chỉ
đo số so sánh khóa, không cài thêm đếm truy cập mảng.

`run_count` là số run tự nhiên **thực sự được gặp trong lượt duyệt**, lấy
độ dài trước khi kéo dài tới minrun. `avg_run_len` là tổng độ dài các run
đã gặp chia số run đó. Các đoạn bị hấp thụ khi mở rộng minrun không được
quét riêng; đây không phải phép phân rã toàn bộ đầu vào thành run. Không
lấy N/run_count làm độ dài trung bình cho định nghĩa này. Mảng rỗng trả
0 và 0.0; một phần tử trả 1 và 1.0. noA để hai chỉ số natural-run `None`.

## Kiểm tra và bàn giao tiếp

```bash
python -B -m unittest tests.test_timsort -v
python -B -m unittest discover -s tests -t . -v
python -m bench.worker --algo timsort-noA --dataset D6 --runs 16 --n 1001 --seed 2026 --mode count --json
```

Bộ test chung đạt 72/72 trên CPython 3.12.13, không skip. Kiểm tra qua
runner với hai thuật toán × 10 cấu hình dữ liệu × 3 chế độ, N=1001,
seed=2026: **60/60 lượt ok**, oracle đúng, input SHA-256 và output_check
khớp giữa ba chế độ. Không lưu CSV cho các lượt kiểm tra này.

Hải nhận giao diện `sort`, `sort_counted`, `sort_noa`, `sort_noa_counted`
đúng tên worker hiện gọi. Thiện review run/noA/stability; Hải review
Powersort stack. Ngân nhận hai bản thảo ở `paper/`. Chưa có xác nhận
review độc lập, số liệu RQ3 chính thức hoặc kết luận thuật toán nhanh hơn.
