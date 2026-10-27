# csd203-sorting-rbl

CSD203 FA26, Đề tài 1: Khảo sát thực nghiệm các thuật toán sắp xếp kinh điển và Timsort (Powersort) trên dữ liệu gần có thứ tự của pipeline AI.

Nhóm: My, Ngân, Hải, Thiện, Dân.

## Bàn giao Ngân ngày 2026-10-28

Bản này mở từ gói tích hợp mới nhất, bổ sung Quick của My từ `Lab`, Merge
của Ngân và kiểm thử review. Chi tiết đóng góp, kết quả kiểm tra và điểm
Radix cần Thiện xác nhận ở `PHAN_CONG.md`; khai báo AI ở `AI_LOG.md`.
Phương pháp Merge để ghép paper: `paper/methods_merge.md`.

Chạy riêng phần kiểm tra bàn giao:

```bash
python -B -m unittest tests.test_merge tests.test_generate tests.test_quick tests.test_radix -v
```

Kiểm chứng nhanh một cấu hình Merge qua worker (đổi `time` thành `mem`
hoặc `count` để kiểm tra hai chế độ còn lại):

```bash
python -B -m bench.worker --algo merge --dataset D1 --n 1001 --seed 2026 --mode time --json
```

Merge đã kiểm tra giao diện với ba chế độ worker. Chưa có
`src/timsort.py` của Dân trong bản này, nên chưa chạy toàn ma trận chính
thức hoặc RQ3; dùng bộ lọc `--algo` cho các module đã có. Không dùng số
liệu chạy thử trên máy phát triển làm kết quả chính thức.

> Bản nháp. Hải bổ sung URL repository, phiên bản 3.12.x chính xác và ngày lịch của các mốc D0–D14.

## Cấu trúc

```text
src/        quick.py (My), merge.py (Ngân), heap.py (Hải), radix.py (Thiện), timsort.py (Dân)
data/       generate.py: bộ sinh D1–D6, input_sha256, output_check
bench/      worker.py, runner.py, make_configs.py, configs.json, plot.py, env_info.py
tests/      test theo từng module
results/    raw/ (CSV gốc), figures/ (hình + summary CSV)
```

## Môi trường

CPython **3.12.x** cho mọi thành viên. Thuật toán, generator và runner chỉ dùng thư viện chuẩn. Matplotlib chỉ dùng cho `bench/plot.py`.

Windows (PowerShell):
```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-plot.txt
```

Linux/macOS:
```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-plot.txt
```

Mọi lệnh bên dưới chạy từ thư mục gốc của repository, sau khi đã kích hoạt `.venv`.

## Kiểm thử

```bash
python -m unittest discover -s tests -t . -v
```

## Ghi thông số máy đo (trước D2)

```bash
python -m bench.env_info --role main --power-mode "Cắm sạc, Best performance"
```

## Đo đạc

```bash
# 1. Sinh lại ma trận (chỉ cần khi đổi phạm vi thí nghiệm)
python -m bench.make_configs --run-id run_main

# 2. Chạy thử nhanh (Heap, Radix, lib-sorted; N = 10.000)
python -m bench.runner --pilot --out results/raw/pilot.csv

# 3. Xem số lượt trước khi chạy
python -m bench.runner --config bench/configs.json --rq RQ2 --dry-run

# 4. Chạy chính thức (máy đo chính, đã commit code, không chạy tác vụ nặng khác)
python -m bench.runner --config bench/configs.json --out results/raw/main.csv --strict-python

# Bị ngắt giữa chừng thì chạy lại đúng lệnh trên, thêm --resume
python -m bench.runner --config bench/configs.json --out results/raw/main.csv --strict-python --resume

# Chỉ chạy một phần, ví dụ các thuật toán đã sẵn sàng
python -m bench.runner --config bench/configs.json --algo heap,radix --out results/raw/main.csv --strict-python --resume
```

Mỗi lượt chạy trong một tiến trình riêng, timeout 60 giây. Mỗi dòng CSV gồm: thuật toán × dữ liệu × seed × chế độ (`time`/`mem`/`count`) × commit.

## Biểu đồ

```bash
python -m bench.plot --csv results/raw/main.csv --rq RQ1
python -m bench.plot --csv results/raw/main.csv --rq RQ2
python -m bench.plot --csv results/raw/main.csv --rq RQ3
```

Kết quả nằm trong `results/figures/`: hình PNG và PDF, `rqX_summary.csv` (median/min/max/n_ok), riêng RQ3 có thêm bảng speedup và ablation.

## Giao diện thuật toán

Mỗi module trong `src/` cung cấp:

- `sort(a) -> None`: sắp xếp tăng dần tại chỗ, không đếm, không log.
- `sort_counted(a) -> dict`: cùng quyết định thuật toán, trả về `key_comparisons`, `array_reads`, `array_writes`, `run_count`, `avg_run_len` (trường không áp dụng trả `None`).

Riêng `src/timsort.py` có thêm `sort_noa(a)` và `sort_noa_counted(a)` cho biến thể noA.
