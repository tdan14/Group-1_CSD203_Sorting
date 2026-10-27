# Phân công và bàn giao phần Ngân

## Cập nhật ngày 2026-10-28

Codex thực hiện theo yêu cầu Ngân. Bản này mở từ `csd203-sorting-rbl.zip`
(Ngân xác nhận là bản tích hợp mới nhất), bổ sung Quick và test Quick từ
`Lab`. Giữ nguyên các gói gốc. Thư mục làm việc chưa có Git/remote; chưa
commit hoặc push. Phần nhật ký My ở cuối là lịch sử bàn giao, không phải
trạng thái hiện tại của toàn bộ bản tích hợp.

### Đầu việc Ngân bàn giao

- **Merge mới:** `src/merge.py`; top-down, một mảng phụ N cho N >= 2,
  ổn định, đủ `sort` và `sort_counted`, đường timing không có bộ đếm.
  **Chờ My review độc lập**, không tự ghi đã được My nghiệm thu.
- **Test Merge mới:** `tests/test_merge.py`; 7 method gồm 5 ca bắt buộc,
  1.000 ca fuzz trên generator thật với đủ 10 cấu hình D1–D6, kích thước
  lẻ/lớn hơn, ổn định 1.000 bản ghi cho cả hai đường chạy, trình tự so
  sánh, số đếm và tái sử dụng buffer. Kế thừa yêu cầu từ bộ test My;
  không dùng mock D4–D6 hoặc skip khi thiếu Merge.
- **Review D4–D6:** thêm 5 method trong lớp `TestGeneratorNganReview` của
  `tests/test_generate.py`. Bao phủ K/R, miền, biên N, tính tái lập, đa
  tập, chia phần dư, lô rỗng, RNG toàn cục và hồi quy D3 seed 2798.
  **Giữ nguyên generator 1.1.0 của Hải/Thiện**, không nhận phần cài đặt
  đã có là đóng góp của Ngân.
- **Review Quick/D1–D3:** giữ nguyên `src/quick.py`; thêm 2 method trong
  lớp `QuickNganReview`, dùng generator thật trên cả ba seed chính thức
  và đối chiếu số so sánh/đọc/ghi với thao tác quan sát độc lập. Các ca
  đã thử đạt; không phát hiện lỗi tính đúng trong phạm vi này.
- **Review Radix:** giữ nguyên `src/radix.py`; thêm 2 method trong lớp
  `RadixNganReview`, dùng generator thật đủ tham số/seed và biên bốn byte.
  Hai đường chạy sắp xếp đúng trên các ca đã thử; review bộ đếm còn mở.
- **Methods:** `paper/methods_merge.md`, tiếng Anh để ghép paper. Có ánh
  xạ hàm/cơ chế, chứng minh ổn định, độ phức tạp, quy ước đếm và phương
  pháp bộ nhớ RQ1; chưa có kết quả đo chính thức.

### Bằng chứng kiểm tra

CPython 3.12.14 trên Windows, máy phát triển. Chạy tại gốc dự án:

```bash
python -B -m unittest discover -s tests -t . -v
```

**38 test method đạt, không skip**; fuzz có nhiều mảng bên trong mỗi
method. Merge còn được gọi qua `bench.runner.run_single_trial` ở đủ 10
cấu hình dữ liệu x 3 chế độ time/mem/count, N = 1001, seed = 2026:
**30/30 lượt ok**, oracle đúng, input SHA-256 và output_check khớp giữa
các chế độ. Không lưu CSV, không dùng thời gian này làm số liệu paper.

### Điểm cần người phụ trách xác nhận

- **Thiện — bộ đếm Radix:** bản thường thực hiện `count[byte_val] -= 1`
  rồi đọc lại `count[byte_val]` trong `output[count[byte_val]] = val`.
  Bản counted giữ vị trí ở biến `pos`, nên ít hơn N lần đọc mỗi lượt
  byte, tổng **4N lần đọc** với N >= 2. Quan sát list qua bản AST trong
  bộ nhớ (không sửa source) cho `[2, 1]`: bản thường 2.088 lượt đọc,
  counted báo 2.080; cả hai 2.078 lượt ghi. N = 10: 2.280 so với 2.240
  lượt đọc; cùng 2.214 lượt ghi. Đây là truy cập mảng logic, không phải
  mọi truy cập nội bộ CPython. Đề nghị Thiện đồng nhất cách dùng `pos`
  hoặc phản ánh lần đọc thứ hai trong counted. Nếu đổi đường timing
  sau khi đã đo, Hải cần xem xét chạy lại cấu hình bị ảnh hưởng.
- **My — Merge:** đọc source và chạy nghiệm thu. Hướng dẫn dùng `<=`
  được thực hiện tương đương bằng chọn phải khi `right < left`, còn
  lại lấy trái, để hỗ trợ bản ghi chỉ có `__lt__` và giữ ổn định.
- **Hải:** ghép vào repository chính thức, ghi commit và môi trường đo.
  Các vấn đề `resume`/hướng dẫn cũ đã nêu trong trao đổi còn cần Hải xử
  lý riêng; chưa sửa runner trong phần Ngân. Bản này chưa có Timsort/noA
  của Dân, không được coi toàn ma trận RQ3 đã chạy được.

Ngân chờ CSV thật để phân tích bộ nhớ RQ1, chờ phần viết các thành viên
để ghép paper. Ngân cần tự đọc, trace và giải thích phần được AI hỗ trợ
trước khi bảo vệ. Kết quả tự động không thay chữ ký review của My/Thiện.

## Nhật ký My giữ lại từ bản bàn giao gốc

**Dự án:** CSD203 Research-Based Learning — Sorting Algorithms & Timsort Study  
**Nhóm 5 thành viên:** My, Ngân, Hải, Thiện, Dân  
**Nhánh làm việc của My:** `rq1-my`

---

## 1. Bảng Phân Công Chi Tiết Của My

| Module / Nhiệm vụ | Vai trò | Người phối hợp / Reviewer | Trạng thái | Commit liên quan | Kết quả kiểm thử / Nghiệm thu |
|---|---|---|---|---|---|
| **Quick Sort** (`src/quick.py`) | Triển khai chính | Ngân (Reviewer) | ✅ Hoàn thành | `rq1-my` | Pass 5 ca bắt buộc + 1.000 ca fuzz (0–200 phần tử, phủ D1–D6), đối chiếu `sorted()`. `sort` và `sort_counted` ra kết quả trùng khớp. Không lặp vô hạn. |
| **Generator D1–D3** (`data/generate.py`) | Triển khai chính | Ngân (Làm D4–D6, Review D1–D3) | ✅ Hoàn thành | `rq1-my` | Pass 7/7 test: D1 đúng miền $[0, 2^{31}-1]$, D2 tăng dần, D3 đúng $\lfloor N/1000 \rfloor$ swap từ luồng `seed + 10000`. Tất định trên seed 2026, 2027, 2028, 203. |
| **Unit & Fuzz Tests** (`tests/`) | Triển khai chính | Ngân (Chạy nghiệm thu) | ✅ Hoàn thành | `rq1-my` | Chạy toàn bộ test `unittest`: 9 tests (gồm 1000 ca fuzz) đạt 100% OK trong < 1s. |
| **Bản thảo Methods Quick** (`paper/methods_quick.md`) | Triển khai chính | Ngân (Ghép bản thảo) | ✅ Hoàn thành | `rq1-my` | Mô tả Hoare partition, Median-of-Three, ánh xạ từng hàm `src/quick.py`, trích dẫn Hoare (1962). |
| **Giả thuyết & Khung RQ1** (`paper/rq1_hypothesis.md`) | Triển khai chính (Thời gian) | Ngân (Bộ nhớ RQ1), Hải (Runner) | ✅ Hoàn thành | `rq1-my` | Lập giả thuyết trước đo cho 4 thuật toán trên D1 ($N = 10k \dots 1M$), công thức throughput, speedup, hướng dẫn xử lý CSV. |
| **Merge Sort** (`src/merge.py`) | Test & Review chéo | Ngân (Triển khai chính) | ⏳ Chờ bàn giao | - | Sẽ test và review ngay khi Ngân push nhánh `rq1-ngan`. |
| **Generator D4–D6** (`data/generate.py`) | Test & Review chéo | Ngân (Triển khai chính) | ⏳ Chờ bàn giao | - | Sẽ kiểm thử D4 (đảo D2), D5 (K giá trị), D6 (R đoạn) khi Ngân hoàn thiện. |
| **Heap Sort** (`src/heap.py`) | Review chéo | Hải (Triển khai chính) | ⏳ Chờ bàn giao | - | Sẽ review thuật toán dựng heap từ dưới lên tại chỗ khi Hải push nhánh `rq2-hai`. |
| **Tích hợp Runner & CSV RQ1** | Phối hợp phân tích | Hải (Tích hợp & chạy benchmark) | ⏳ Chờ mốc D8–D10 | `rq1-my` | `bench/plot_rq1.py` + `bench/sample_rq1_data.csv` + `requirements-plot.txt` đã sẵn sàng; khi có CSV thật từ Hải (D8–D10) chạy `python bench/plot_rq1.py results/raw/rq1_benchmark.csv` để ra 2 hình trong `results/figures/`. |
| **Review test Merge Sort** (`tests/test_merge.py`) | Triển khai chính | Ngân (Chạy review) | ✅ Hoàn thành | `rq1-my` | 5 ca cố định + 1.000 fuzz + Stability (1.000 Record(key,order)); skip an toàn khi `src/merge.py` chưa có (import có điều kiện). |
| **Hạn chế Quick Sort** (`paper/limitations_quick.md`) | Triển khai chính | Ngân (Ghép paper) | ✅ Hoàn thành | `rq1-my` | 4 mục IEEE: Unstability, O(N) stack, CPython constant/cache, no-cutoff (quy định đề bài). |
| **Ôn tập vấn đáp** (`docs/ON_TAP_VAN_DAP_MY.md`) | Triển khai chính | - | ✅ Hoàn thành | `rq1-my` | Trace [5,1,6,2,10,3] & [3,3,3], chứng minh lo <= j < hi, 10 câu hỏi + câu trả lời chuẩn 4 điểm. |

---

## 2. Nhật Ký Tiến Độ Phiên Làm Việc (My)

- **Mốc D3–D5 (Chuẩn bị trước):**
  - Xây dựng sẵn bộ test review `tests/test_merge.py` (5 ca fixed, 1.000 ca fuzz, Stability test) chạy độc lập, tự động skip an toàn khi Ngân chưa bàn giao.
  - Xây dựng pipeline phân tích & vẽ biểu đồ tự động `bench/plot_rq1.py`, kèm mock CSV đủ 27 cột `bench/sample_rq1_data.csv` và `requirements-plot.txt`. Sinh thành công 2 biểu đồ PNG vào `results/figures/`.
  - Soạn thảo phần Hạn chế của Quick Sort `paper/limitations_quick.md` theo chuẩn bài báo IEEE.
  - Biên soạn tài liệu ôn tập vấn đáp cá nhân `docs/ON_TAP_VAN_DAP_MY.md` với 2 bài trace mẫu và 10 câu hỏi chuyên sâu.
- **Mốc D0–D2:**
  - Khởi tạo cấu trúc dự án, tạo nhánh `rq1-my`.
  - Hoàn thành module Quick Sort với phân hoạch Hoare và Median-of-Three pivot tại chỗ.
  - Hoàn thành generator D1–D3 đạt chuẩn giao diện chung `generate(dataset, n, seed, k=None, runs=None)`.
  - Xây dựng bộ test bắt buộc (`tests/test_quick.py`, `tests/test_generate.py`) với 1.000 ca fuzz.
  - Viết bản thảo Methods Quick Sort và Giả thuyết RQ1 sẵn sàng ghép nối vào báo cáo paper IEEE.
- **Vướng mắc kỹ thuật:** Không có. Code chạy hoàn toàn trên thư viện chuẩn Python (CPython stdlib), tương thích tốt từ Python 3.10 đến Python 3.12+.
- **Kế hoạch phiên tiếp theo:**
  - Bàn giao `data/generate.py` cho Ngân để triển khai D4–D6.
  - Ghép `src/quick.py` vào runner của Hải khi Hải cung cấp khung `bench/runner.py` (trước D3–D4).
  - Tiếp nhận và review chéo Merge Sort của Ngân.
