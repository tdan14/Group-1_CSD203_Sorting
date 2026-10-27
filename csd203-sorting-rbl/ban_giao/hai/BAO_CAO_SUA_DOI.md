# Báo cáo sửa đổi gói bàn giao Runner/RQ2

> Người thực hiện: Hải (`rq2-hai`), có dùng AI hỗ trợ (ghi vào `AI_LOG.md`)
> Người cần review: Thiện (`rq2-thien`)
> Căn cứ: Đề tài 1 CSD203 FA26 và proposal nhóm (Phần II)

## 1. Tóm tắt

| File | Trạng thái | Nội dung chính |
|---|---|---|
| `src/heap.py` | **Mới** | Heap Sort: max-heap tại chỗ, dựng heap bottom-up, có `sort` và `sort_counted` |
| `data/generate.py` | Sửa | D3 hoán đổi **hai vị trí phân biệt**; `GENERATOR_VERSION` lên `1.1.0` |
| `bench/worker.py` | Sửa | Ghi mốc phase, chuẩn hóa tên thuật toán, nhận commit từ runner |
| `bench/runner.py` | Viết lại | Phase khi timeout, định danh đầy đủ, lọc cấu hình, `--resume`, kiểm tra Python 3.12 |
| `bench/make_configs.py` | **Mới** | Sinh ma trận cả RQ1–RQ3, gộp cấu hình trùng |
| `bench/configs.json` | Tạo lại | 1.308 lượt (RQ1 180, RQ2 720, RQ3 840; 396 lượt dùng chung) |
| `bench/plot.py` | Viết lại | Median/min/max, số lượt ok, tách theo dataset, biểu đồ đếm, ablation RQ3 |
| `bench/env_info.py` | **Mới** | Tự đọc CPU/RAM/OS/Python để ghi `environment.json` |
| `tests/test_heap.py` | Sửa | Fuzz 1.000 ca phủ đủ D1–D6 (cả 3 mức K và R) |
| `tests/test_generate.py` | **Mới** | Kiểm tra từng quy ước của generator |
| `src/radix.py`, `tests/test_radix.py` | Giữ nguyên | Đã đúng đặc tả |

Kết quả kiểm thử trên CPython 3.12.3: **20/20 test đạt** (`python -m unittest discover -s tests -t .`).

## 2. Chi tiết từng lỗi đã sửa

### 2.1 Generator D3: hoán đổi trùng vị trí
- **Lỗi:** `i` và `j` lấy bằng hai lần `randint` độc lập nên có thể trùng nhau, khi đó lần hoán đổi không có tác dụng. Proposal yêu cầu "hoán đổi hai vị trí phân biệt".
- **Sửa:** `i, j = swap_rng.sample(range(n), 2)`.
- **Ảnh hưởng đến dữ liệu:** `sample` dùng cùng luồng ngẫu nhiên với hai lần `randint` và chỉ rút lại khi trùng. Đã kiểm chứng: với seed 2026/2027/2028 ở N = 100.000 và 1.000.000, D3 **giống hệt từng bit** bản cũ (không có lần trùng nào). Ví dụ một trường hợp đã được sửa: seed 2798, N = 1000. D1, D2, D4, D5, D6 không đổi.
- Vẫn tăng phiên bản lên `1.1.0` vì hành vi của code đã khác.

### 2.2 Runner ghi sai `phase` khi timeout hoặc crash
- **Lỗi:** luôn ghi `phase="sort"`, không phân biệt được tiến trình bị ngắt khi đang sinh dữ liệu hay khi đang sắp xếp. Đề yêu cầu phân biệt hai trường hợp này.
- **Sửa:** worker in `PHASE:prepare|sort|validate` ra stderr (flush ngay, không in gì trong vùng đo). Khi timeout, runner đọc mốc cuối cùng trong `TimeoutExpired.stderr`.
- **Đã thử:** heap N = 1M với timeout 3 s cho `phase=sort`; radix D5 N = 1M với timeout 0,3 s cho `phase=prepare`.

### 2.3 Dòng lỗi thiếu định danh
- **Lỗi:** dòng timeout/crash để trống `code_commit`, `machine_id`, `python_version`, `generator_version`.
- **Sửa:** runner điền đủ 4 trường cho mọi dòng. Runner lấy commit một lần rồi truyền xuống worker (`--code-commit`), nên mọi dòng trong một lượt chạy có cùng commit. Nếu còn thay đổi chưa commit, commit được ghi kèm hậu tố `-dirty` và runner in cảnh báo.

### 2.4 Phân loại lỗi
- `oom` chỉ ghi khi thấy đúng `MemoryError`.
- Tiến trình bị hệ điều hành kill (ví dụ OOM killer, tín hiệu 9) được ghi `crash` với `error_type=Signal9`, **không** tự suy ra `oom` (đúng quy định "không tự suy đoán oom").
- Ngoại lệ khác: lấy đúng tên lớp lỗi từ traceback (ví dụ `RecursionError`, `ModuleNotFoundError`).

### 2.5 Tính năng runner còn thiếu
- **Lọc cấu hình:** docstring cũ nói có lọc nhưng code chưa có. Nay có `--rq --algo --dataset --n --mode --seed`.
- **Chạy tiếp:** `--resume` bỏ qua các lượt đã có trong CSV với cùng commit và cùng máy. Hữu ích vì toàn bộ ma trận chạy mất vài giờ.
- **Kiểm tra phiên bản:** cảnh báo khi không phải CPython 3.12; thêm `--strict-python` để dừng hẳn. Dùng cờ này cho lượt đo chính thức.
- `--dry-run`: chỉ đếm số lượt sẽ chạy.

### 2.6 Ma trận cấu hình
- `configs.json` cũ chỉ có RQ2. File hướng dẫn ghi "4 × 6 phân phối × 2 × 3 × 3 = 720" là tính sai (phép nhân đó ra 432). Con số 720 đúng vì có **10 cấu hình dữ liệu**: D1–D4, ba mức K của D5, ba mức R của D6.
- `make_configs.py` sinh cả 3 RQ và gộp các lượt trùng. Trường `rq` ghi mọi RQ dùng lượt đó, ví dụ `RQ1+RQ2+RQ3`.
- Đã kiểm tra: phần RQ2 của file mới trùng khớp 720 cấu hình cũ của Thiện.

### 2.7 `plot.py`
- Biểu đồ bộ nhớ cũ gộp cả 10 dataset vào một cột cho mỗi thuật toán; nay tách theo dataset.
- Thêm thanh lỗi min–max, ghi `2/3` khi thiếu lượt ok, ghi `n/a` khi không lượt nào đạt (bản cũ vẽ cột bằng 0, dễ hiểu lầm).
- Dừng và báo lỗi nếu CSV lẫn nhiều máy, commit, phiên bản Python hoặc generator; chọn lại bằng `--machine` / `--commit`.
- Thêm biểu đồ đếm phép toán: (a) số phép so sánh khóa, (b) số lượt đọc mảng. Radix chỉ nằm ở (b), đúng yêu cầu không đặt đọc/ghi của Radix ngang số so sánh.
- RQ1: biểu đồ đường theo N (trục log). RQ3: biểu đồ ablation `(T_noA − T_timsort)/T_noA × 100%` và bảng speedup.
- Mỗi lần vẽ đều xuất `*_summary.csv` (median/min/max/n_ok) để truy từ hình về CSV.
- Màu cố định theo thuật toán; hai thứ tự màu đã qua kiểm tra phân biệt cho người mù màu. Có thêm hoa văn (hatch) để in đen trắng vẫn đọc được.
- Xuất cả PNG 300 dpi và PDF cho paper IEEE.

## 3. Heap Sort (`src/heap.py`)
- Dựng heap: `for start in range(n//2 - 1, -1, -1)`, đúng "từ N/2 lùi về 0".
- Sift-down dùng kỹ thuật lỗ hổng: giữ phần tử đang chìm trong biến, chỉ chép con lớn hơn lên, ghi một lần ở cuối. Số phép so sánh giống cách hoán đổi từng tầng nhưng ít lần ghi mảng hơn.
- `sort_counted` đếm từng phép `<`, từng lần đọc `a[i]` và ghi `a[i]`, với cùng thứ tự quyết định như `sort`. `run_count` và `avg_run_len` trả `None`.
- Bộ nhớ phụ đo bằng tracemalloc ở N = 10.000: 228 byte (đúng tính chất tại chỗ).

## 4. Việc cần phối hợp với các thành viên khác
- **Dân:** worker gọi `src/timsort.py` với các hàm `sort`, `sort_counted`, `sort_noa`, `sort_noa_counted`. Cần xác nhận đúng 4 tên này. Với noA, `run_count`/`avg_run_len` trả `None`.
- **My, Ngân:** `src/quick.py`, `src/merge.py` cần có `sort` và `sort_counted` như Heap/Radix.
- **Thiện:** review `heap.py` và `test_heap.py`, đồng thời chạy lại toàn bộ test trên máy dự phòng bằng **Python 3.12**.
- **Cả nhóm:** cài cùng một bản CPython 3.12.x.

## 5. Chưa làm (ngoài phạm vi bản sửa này)
- Chưa tạo Git repository, `README` chính thức, `PHAN_CONG.md`, `AI_LOG.md`.
- Chưa chạy đo chính thức: còn thiếu Quick, Merge, Timsort và cần chạy trên máy đo chính.
