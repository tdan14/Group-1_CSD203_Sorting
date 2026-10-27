# CSD203 Sorting RBL

Nhóm My, Ngân, Hải, Thiện và Dân. Bản tích hợp ngày **28/10/2026**.

Đã ghép Quick của My, Merge của Ngân, Heap của Hải, Radix của Thiện và
runner/worker/generator từ gói bàn giao. Các file này giữ nguyên nội dung,
không sửa logic. Dân có thêm Timsort/Powersort, noA và các hàm counted.

Chi tiết nguồn từng file và các điểm nhóm cần xem sau ở
[docs/TICH_HOP.md](docs/TICH_HOP.md). Toàn bộ 97 file bàn giao được giữ tại
[ban_giao/](ban_giao/README.md), gồm cả test cũ, AI log, tài liệu cá nhân,
bản thảo, CSV mẫu và hình minh họa của My.

## Chạy từ đâu

Mở terminal tại thư mục có README này, tức `csd203-sorting-rbl/`.
Dùng **CPython 3.12.x**, thống nhất patch version với máy đo của Hải trước
khi thu số liệu chính thức. Core và bộ test chỉ dùng thư viện chuẩn.

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -B -X utf8 -m unittest discover -s tests -t . -v
.venv\Scripts\python.exe -B -X utf8 -m scripts.check_ready
.venv\Scripts\python.exe -B -m scripts.check_submissions
```

Sau khi kích hoạt venv, có thể dùng `python` thay đường dẫn trên.
Trên Linux/macOS, dùng `python3.12 -m venv .venv` và `.venv/bin/python`.
`-X utf8` giúp terminal Windows hiển thị tiếng Việt.

## Thử một lượt qua worker

```bash
python -m bench.worker --algo quick --dataset D1 --n 1001 --seed 2026 --mode time --json
python -m bench.worker --algo timsort --dataset D6 --runs 16 --n 1001 --seed 2026 --mode mem --json
python -m bench.worker --algo timsort-noA --dataset D5 --k 10 --n 1001 --seed 2026 --mode count --json
```

Tên thuật toán: `quick`, `merge`, `heap`, `radix`, `timsort`,
`timsort-noA`, `lib-sorted`. `lib-sorted` chỉ có `time` và `mem`.
Worker in JSON ra stdout, phase ra stderr, không tự lưu CSV.

## Chạy bằng runner của Hải

```bash
python -m bench.runner --pilot --out results/smoke/pilot.csv
python -m bench.runner --config bench/configs.json --rq RQ3 --dry-run
python -m bench.runner --config bench/configs.json --algo timsort,timsort-noA --dataset D6 --n 100000 --seed 2026 --mode time --out results/smoke/dan.csv
```

`--dry-run` chỉ đếm công việc, không thực hiện phép đo. Runner hiện dùng
`--algo`, `--config`, `--mode`; đây là giao diện trong gói Hải bàn giao.
Các lệnh `--algorithm`, `--official`, `--mem`, `--count` của bộ khung cũ
không áp dụng cho runner hiện tại.

Trước benchmark chính thức, Hải kiểm tra môi trường và commit code:

```bash
python -m bench.env_info --role main --power-mode "Ghi đúng chế độ nguồn thực tế"
python -m bench.runner --config bench/configs.json --out results/raw/main.csv --strict-python
```

Ma trận dùng seed 2026/2027/2028, mỗi lượt có timeout 60 giây và chạy trong
tiến trình riêng. Đây là công việc thu số liệu của nhóm; bản tích hợp chưa
chạy toàn ma trận. Dùng tên CSV mới cho mỗi đợt. Các lưu ý về `--resume`
và trạng thái lỗi trong bàn giao vẫn cần Hải review.

## Biểu đồ và bản thảo

```bash
python -m pip install -r requirements-plot.txt
python -m bench.plot --csv results/raw/main.csv --rq RQ1
python -m bench.plot --csv results/raw/main.csv --rq RQ2
python -m bench.plot --csv results/raw/main.csv --rq RQ3
```

Giữ nguyên `bench/plot.py` của Hải và `bench/plot_rq1.py` của My.
Hai gói gốc khai báo phiên bản Matplotlib khác nhau; nhóm thống nhất môi
trường vẽ sau. CSV và hình mẫu của My nằm trong `ban_giao/my/`, không phải
kết quả đo chính thức. `bench/summarize.py` giữ từ bộ khung cũ; luồng vẽ
hiện tại dùng trực tiếp CSV thô qua `bench.plot` như trên.

Các phần viết đã có ở `paper/`: Quick, Merge, giả thuyết RQ1 và phần
Timsort/RQ3 mới. Nhóm cần CSV thật để viết kết quả và hoàn thiện paper.

## Tài liệu bàn giao

- [Thiện → Hải](HUONG_DAN_CHO_HAI.md).
- [My → Ngân](BAO_CAO_BAN_GIAO_MY_CHO_NGAN.md).
- [Báo cáo sửa đổi của Hải](BAO_CAO_SUA_DOI.md).
- [Bàn giao Ngân](ban_giao/ngan/PHAN_CONG.md).
- [Bàn giao Dân](BAO_CAO_BAN_GIAO_DAN.md).
- [Phân công chung](PHAN_CONG.md), [AI log chung](AI_LOG.md).
- [Ôn tập My](docs/ON_TAP_VAN_DAP_MY.md), [ôn tập Dân](docs/ON_TAP_VAN_DAP_DAN.md).

Tài liệu gốc giữ lại lịch sử và trạng thái tại thời điểm từng người bàn
giao. Trạng thái tích hợp hiện tại được ghi trong `docs/TICH_HOP.md`.
