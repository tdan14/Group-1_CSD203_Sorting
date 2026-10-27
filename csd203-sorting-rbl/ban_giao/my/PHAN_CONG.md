# Bảng Phân Công Công Việc & Nhật Ký Đóng Góp

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
