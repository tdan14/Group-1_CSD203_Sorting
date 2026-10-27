# CSD203 Sorting Algorithms & Timsort RBL Study

Nghiên cứu thực nghiệm so sánh các thuật toán sắp xếp kinh điển (Quick Sort, Merge Sort, Heap Sort, Radix Sort) và Timsort (dùng Powersort) trên dữ liệu pipeline AI.

**Nhóm nghiên cứu 5 thành viên:** My, Ngân, Hải, Thiện, Dân.  
**Nhánh làm việc của My:** `rq1-my`

---

## 1. Cấu Trúc Dự Án (Phần Đảm Nhiệm Của My)

- `src/quick.py`: Cài đặt Quick Sort dùng phân hoạch Hoare kết hợp chọn pivot Median-of-Three tại chỗ, không cutoff, tuân thủ giao diện `sort(a)` và `sort_counted(a)`.
- `data/generate.py`: Bộ sinh dữ liệu thực nghiệm D1 (ngẫu nhiên), D2 (tăng dần), D3 (gần tăng dần với $\lfloor N/1000 \rfloor$ swap). D4–D6 do Ngân triển khai.
- `tests/test_quick.py`: Bộ kiểm thử bắt buộc cho Quick Sort gồm 5 ca biên/cố định và 1.000 ca ngẫu nhiên phủ D1–D6 đối chiếu `sorted()`.
- `tests/test_generate.py`: Kiểm thử bộ sinh dữ liệu D1–D3 (tính tất định, miền giá trị, số lượng hoán đổi).
- `paper/methods_quick.md`: Bản thảo phần Phương pháp Quick Sort phục vụ bài báo IEEE (ánh xạ trực tiếp tới code và trích dẫn Hoare 1962).
- `paper/limitations_quick.md`: Bản thảo phần Hạn chế và Đánh đổi kiến trúc của Quick Sort chuẩn IEEE.
- `paper/rq1_hypothesis.md`: Giả thuyết định lượng RQ1 và quy trình phân tích thời gian thực thi / throughput từ file CSV benchmark.
- `bench/plot_rq1.py`: Script phân tích số liệu RQ1 và tự động sinh 2 biểu đồ đường thời gian & biểu đồ cột throughput chuẩn IEEE từ CSV.
- `bench/sample_rq1_data.csv`: File CSV dữ liệu giả lập đủ schema 27 cột phục vụ kiểm thử script vẽ biểu đồ.
- `requirements-plot.txt`: Danh sách gói phục vụ riêng cho script vẽ biểu đồ ngoài vùng đo (chứa matplotlib).
- `tests/test_merge.py`: Bộ kiểm thử độc lập phục vụ review Merge Sort của Ngân (5 ca fixed, 1.000 ca fuzz, test ổn định).
- `docs/ON_TAP_VAN_DAP_MY.md`: Cẩm nang ôn tập vấn đáp cá nhân (4/4 điểm bảo vệ D14) với 2 bài trace mẫu và 10 câu hỏi chuyên sâu.
- `PHAN_CONG.md`: Bảng theo dõi phân công, trạng thái công việc và nhật ký đóng góp.
- `AI_LOG.md`: Nhật ký tương tác AI, phân loại chấp nhận / sửa đổi / bác bỏ và bằng chứng kiểm chứng.

---

## 2. Yêu Cầu Môi Trường

- **Mục tiêu thực nghiệm môn học:** CPython 3.12 (môi trường ảo venv, đơn luồng).
- **Khả năng tương thích:** Toàn bộ mã nguồn của My được viết bằng Python thuần túy (standard library), chạy hoàn hảo trên CPython 3.10 trở lên mà không cần thư viện ngoài.
- *Ngoại lệ duy nhất:* `matplotlib` (pin trong `requirements-plot.txt`) chỉ dùng trong `bench/plot_rq1.py` để vẽ hình từ CSV — nằm ngoài vùng đo, theo quy định đề bài (dòng 417 proposal).
- *Lưu ý:* Thông số phần cứng và môi trường máy đo chính thức do Hải quản lý và cập nhật tại `environment.json`.

---

## 3. Hướng Dẫn Chạy & Kiểm Thử

### A. Chạy Toàn Bộ Kiểm Thử
```bash
python -m unittest tests.test_quick tests.test_generate -v
```

### B. Chạy Thử Sinh Dữ Liệu D1–D3
```bash
python -c "from data.generate import generate; print('D1 sample:', generate('D1', 10, 2026))"
python -c "from data.generate import generate; print('D2 sample:', generate('D2', 10, 2026))"
python -c "from data.generate import generate; print('D3 sample:', generate('D3', 10, 2026))"
```

### C. Chạy Thử Quick Sort (Đo đếm phép toán)
```bash
python -c "import src.quick as q; a=[0, 2147483647, 0]; res=q.sort_counted(a); print('Sorted:', a); print('Counters:', res)"
```

### D. Chạy Bộ Test Review Merge Sort
```bash
python -m unittest tests.test_merge -v
```
*(Ghi chú: Bộ test tự động skip toàn bộ an toàn khi `src/merge.py` chưa được Ngân bàn giao).*

### E. Vẽ Biểu Đồ RQ1 từ CSV (Mock hoặc Thật)
```bash
pip install -r requirements-plot.txt
python bench/plot_rq1.py bench/sample_rq1_data.csv
```
*(Xem 2 file biểu đồ PNG xuất ra tại thư mục `results/figures/`).*
