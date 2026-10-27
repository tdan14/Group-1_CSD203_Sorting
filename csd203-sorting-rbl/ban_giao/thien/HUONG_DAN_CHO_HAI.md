# TÀI LIỆU BÀN GIAO & HƯỚNG DẪN TÍCH HỢP (THIỆN GỬI HẢI)

> **Người gửi**: Thiện (`rq2-thien`)  
> **Người nhận**: Hải (`rq2-hai`)  
> **Đề tài**: CSD203 Sorting RBL - Khảo sát thực nghiệm các thuật toán sắp xếp  
> **Phạm vi phụ trách chung**: Cặp Hải – Thiện (phụ trách Heap, Radix, hệ thống Runner/Worker và nghiên cứu RQ2).

---

## 1. Danh sách file và thành phần bàn giao

Toàn bộ các file trong thư mục này đã được Thiện kiểm thử chạy thành công 100%:

```text
ban_giao_hai/
├── HUONG_DAN_CHO_HAI.md         # File này: hướng dẫn chi tiết cách dùng và tích hợp
├── requirements-plot.txt       # Phiên bản thư viện vẽ biểu đồ (matplotlib==3.11.2)
├── environment_thien.json      # Thông số máy của Thiện (dự phòng theo quy chế đề bài)
├── src/
│   └── radix.py                # Thuật toán LSD Radix Sort 256 (đủ hàm sort & sort_counted)
├── data/
│   └── generate.py             # Bộ sinh D1–D6, tính SHA-256 đầu vào & checksum đầu ra
├── bench/
│   ├── worker.py               # Worker chạy từng lượt đo độc lập (time, mem, count)
│   ├── runner.py               # Runner điều phối đa tiến trình, timeout 60s & xuất CSV
│   ├── plot.py                 # Script vẽ biểu đồ nghiên cứu RQ2 từ CSV
│   └── configs.json            # Ma trận 720 cấu hình thực nghiệm hoàn chỉnh cho RQ2
└── tests/
    ├── test_radix.py           # Unit test Radix (100% ca biên + 1.000 test ngẫu nhiên)
    └── test_heap.py            # Unit test Heap Sort (Thiện chuẩn bị sẵn cho Hải kiểm thử)
```

---

## 2. Hướng dẫn sử dụng & Tích hợp chi tiết

### Bước 1: Kiểm tra nhanh thuật toán Radix Sort
Hải có thể chạy lệnh sau để kiểm tra tính đúng đắn của `src/radix.py`:
```bash
python3 -m unittest tests/test_radix.py
```
*Kết quả chuẩn*: Chạy xong trong ~0.15 giây, vượt qua toàn bộ ca biên (`[]`, `[7]`, `[2, 1]`, `[3, 3, 3]`, `[0, 2147483647, 0]`) và 1.000 mảng ngẫu nhiên.

---

### Bước 2: Tích hợp Heap Sort của Hải (`src/heap.py`)
Hải chỉ cần đặt file code Heap Sort vào `src/heap.py`. Trong file đó cung cấp đủ 2 hàm theo đúng giao diện đã thống nhất:
1. `def sort(a: list[int]) -> None`:
   - Dựng max-heap từ dưới lên (bottom-up), sắp xếp tại chỗ mảng `a`.
   - Không dùng thư viện `heapq`.
   - Không in log, không bật bộ đếm thời gian/phép toán bên trong hàm này.
2. `def sort_counted(a: list[int]) -> dict`:
   - Cùng logic sắp xếp như `sort(a)`.
   - Trả về dictionary:
     ```python
     {
         "key_comparisons": int,   # Số phép so sánh khóa thực tế
         "array_reads": int,        # Số lần đọc phần tử mảng
         "array_writes": int,       # Số lần ghi phần tử mảng
         "run_count": None,         # Không áp dụng cho Heap
         "avg_run_len": None        # Không áp dụng cho Heap
     }
     ```

> [!TIP]
> **Kiểm tra Heap Sort của Hải**: Hải có thể dùng ngay file [`tests/test_heap.py`](file:///home/thien/Downloads/CSD/ban_giao_hai/tests/test_heap.py) mà Thiện đã viết sẵn để test:
> ```bash
> python3 -m unittest tests/test_heap.py
> ```

---

### Bước 3: Vận hành Runner & Thu thập dữ liệu CSV

Hệ thống đo lường trong `bench/` đã được Thiện tích hợp toàn diện các quy định của đề bài:
- **Tiến trình cô lập**: Mỗi lượt đo chạy trong một subprocess riêng.
- **Timeout 60s**: Tự động ngắt khi vượt quá 60s và ghi nhận trạng thái `status = "timeout"`.
- **Đo bộ nhớ đỉnh (`mode="mem"`)**: Dùng `tracemalloc`, tự động tắt tracing trước khi kiểm tra oracle để không làm sai lệch bộ nhớ của thuật toán.
- **Tính Checksum**: Tự động tính hash $h = (31 \times h + x) \pmod{2^{64}}$ ghi vào cột `output_check`.
- **Chuẩn hóa CSV**: Xuất đúng thứ tự 4 nhóm cột theo quy định trang 9 của tài liệu đề tài.

#### Cách chạy:
1. **Chạy thử một cấu hình đơn lẻ bằng Worker**:
   ```bash
   # Đo thời gian
   python3 -m bench.worker --algo radix --dataset D1 --n 100000 --seed 2026 --mode time
   
   # Đo bộ nhớ
   python3 -m bench.worker --algo radix --dataset D1 --n 100000 --seed 2026 --mode mem
   
   # Đo phép toán
   python3 -m bench.worker --algo radix --dataset D1 --n 100000 --seed 2026 --mode count
   ```
2. **Chạy thử nghiệm Pilot (kiểm tra nhanh Runner & Worker)**:
   ```bash
   python3 -m bench.runner --pilot --out results/raw/pilot.csv
   ```
3. **Chạy ma trận thực nghiệm chính thức cho RQ2**:
   Khi Hải đã có đủ các thuật toán trên máy đo chính, Hải chạy toàn bộ 720 cấu hình bằng lệnh:
   ```bash
   python3 -m bench.runner --config bench/configs.json --out results/raw/rq2_official.csv --timeout 60
   ```

---

### Bước 4: Tạo biểu đồ nghiên cứu RQ2 phục vụ bài báo

Sau khi có file CSV kết quả, Hải (hoặc Thiện) chỉ cần chạy script `bench/plot.py`:
```bash
# Vẽ biểu đồ cho N = 100.000
python3 -m bench.plot --csv results/raw/rq2_official.csv --n 100000 --out-dir results/figures/

# Vẽ biểu đồ cho N = 1.000.000
python3 -m bench.plot --csv results/raw/rq2_official.csv --n 1000000 --out-dir results/figures/
```
Script sẽ tự động tạo 2 biểu đồ chuẩn chất lượng cao trong `results/figures/`:
1. `rq2_throughput_N{n}.png`: So sánh Throughput giữa các thuật toán trên D1–D6.
2. `rq2_memory_N{n}.png`: So sánh bộ nhớ đỉnh giữa các thuật toán.

---

### Bước 5: Thông số máy đo & Dự phòng

Theo quy định tại Trang 7 của đề bài: máy của Hải là máy đo chính. Nếu máy của Hải gặp sự cố không khả dụng, toàn bộ lượt đo chính thức sẽ được chuyển sang máy của Thiện.
- Thông số máy của Thiện đã được ghi lại trong file [`environment_thien.json`](file:///home/thien/Downloads/CSD/ban_giao_hai/environment_thien.json) (CPU Intel Core Ultra 5 250K Plus, 32GB RAM, Ubuntu Linux).
- Khi Hải khởi tạo `environment.json` trên máy đo chính, hãy ghi thông số phần cứng của Hải vào file đó trước D2.

---

## 3. Giải thích cụ thể về 2 file JSON đính kèm

Để Hải không bị bỡ ngỡ khi thấy các file `.json`, Thiện giải thích rõ mục đích của từng file:

### 1. File `environment_thien.json` (Thông số máy của Thiện)
- **Nội dung**: Lưu thông số phần cứng máy tính của Thiện (CPU Intel Core Ultra 5 250K Plus, 32GB RAM, Ubuntu Linux, Python 3.14).
- **Mục đích**: Theo quy chế tại **Trang 7 của đề bài**, máy của Hải làm máy đo chính, máy Thiện làm **máy đo dự phòng**. File này lưu sẵn thông số của Thiện để phòng trường hợp máy Hải gặp sự cố thì cả nhóm dùng máy Thiện đo mà không bị vi phạm quy chế (không được trộn số liệu 2 máy).
- **Hải cần làm gì?**: Hải dùng lệnh `environment.json` trên máy Hải để lưu thông số máy Hải trước mốc D2 theo phân công.

### 2. File `bench/configs.json` (Ma trận 720 bài test tự động cho RQ2)
- **Nội dung**: Chứa danh sách 720 cấu hình thử nghiệm đầy đủ cho RQ2 (kết hợp của 4 thuật toán × 6 phân phối D1–D6 × 2 kích thước 100k, 1M × 3 seeds × 3 modes).
- **Mục đích**: Giúp Hải không phải viết vòng lặp hay gõ lệnh thủ công 720 lần.
- **Hải cần làm gì?**: Khi đã có đủ thuật toán, Hải chỉ cần chạy duy nhất một lệnh:
  ```bash
  python3 -m bench.runner --config bench/configs.json --out results/raw/rq2_official.csv
  ```
  Hệ thống sẽ tự động chạy tuần tự toàn bộ 720 bài test, tự ngắt sau 60s nếu treo, và xuất thẳng ra file CSV cho hai đứa mình lấy số liệu phân tích RQ2.

---

## 4. Liên hệ & Phối hợp
Mọi commit và cập nhật tiến độ, hai đứa mình nhớ ghi nhận vào file `PHAN_CONG.md` để giảng viên chấm điểm đóng góp cá nhân nhé! Có vướng mắc gì ở khâu tích hợp runner hay worker thì báo Thiện hỗ trợ ngay.
