# CSD203 Sorting RBL

Repo khởi động cho nhóm **My, Ngân, Hải, Thiện và Dân**, theo proposal Sorting đã thống nhất. Mục tiêu: khảo sát thuật toán theo quy mô và cấu trúc dữ liệu, đánh giá Timsort/Powersort và bóc tách nhận diện run.

**Đã có:** generator D1–D6, giao diện/registry, cấu hình 3 RQ, runner dùng subprocess, các mode đo, checksum/oracle, test khung, summary, script vẽ timing, phân công và tài liệu cộng tác.

**Nhóm cần làm:** Quick/Merge/Heap/Radix/Timsort/noA và đường counted đang TODO. Chưa có số liệu nghiên cứu hoặc paper hoàn chỉnh. Các module không dùng sorted giả làm thuật toán; benchmark chính thức bị chặn khi thiếu module. `lib-sorted` chạy ngay để kiểm tra hạ tầng.

## 1. Bắt đầu trên Windows

Cài **CPython 3.12**. Mở terminal tại thư mục có README này:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe -m bench.runner --algorithm lib-sorted --dataset D1 --n 1000
```

Không cần kích hoạt PowerShell script; các lệnh gọi trực tiếp Python của venv. Core không có dependency ngoài. `requirement.txt` là alias tương thích; `requirements.txt` là tên chuẩn dùng trong hướng dẫn.

Nếu đã kích hoạt venv, thay `.venv\Scripts\python.exe` bằng `python` trong các ví dụ tiếp theo. Chạy mọi lệnh từ **repo root**, dùng `python -m bench.runner`, không chạy trực tiếp `python bench/runner.py`.

macOS/Linux:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m bench.runner --algorithm lib-sorted --dataset D1 --n 1000
```

## 2. Ai bắt đầu từ đâu

| Người | Việc đầu tiên | Review |
|---|---|---|
| My | src/quick.py; đọc/review data/generate.py D1–D3 | Merge; Heap |
| Ngân | src/merge.py; generator D4–D6 | Quick; Radix |
| Hải | src/heap.py; review runner/worker; tạo Git repo | Radix và mem/count; Powersort stack |
| Thiện | src/radix.py; review mem/count/CSV | Heap và timing/timeout; run/noA |
| Dân | src/timsort.py: Timsort/Powersort và noA, stability | Quick/Merge; ablation |

Đọc [bối cảnh](docs/BOI_CANH.md), [proposal](docs/PROPOSAL.md), [quy ước kỹ thuật](docs/QUY_UOC_KY_THUAT.md), [phân công](PHAN_CONG.md) và [cách cộng tác](CONTRIBUTING.md). Hạ tầng có sẵn vẫn cần chủ module kiểm chứng và ghi đóng góp.

## 3. Cấu trúc

| Thư mục/file | Nội dung |
|---|---|
| src/ | Thuật toán TODO, registry và hợp đồng metric |
| data/ | Generator tham chiếu và checksum |
| tests/ | Test generator/harness; fuzz/edge/stability tự kích hoạt khi module sẵn sàng |
| bench/ | Worker/runner, configs, summary và plot |
| scripts/ | Kiểm tra bàn giao và ghi nhận môi trường |
| results/ | raw, summary, figures; smoke bị loại khỏi Git |
| docs/ | Bối cảnh, proposal, quy ước và tiến độ |
| paper/ | Outline paper, hướng dẫn và nơi lưu slide |
| environment.json | Mẫu môi trường, chưa ghi phần cứng thật |
| PHAN_CONG.md, AI_LOG.md | Trách nhiệm và bằng chứng kiểm chứng |
| .github/ | Mẫu PR và issue dùng khi đưa lên GitHub |

## 4. Triển khai và test

1. Viết `sort(a) -> None` sửa danh sách tại chỗ, không bộ đếm.
2. Viết `sort_counted(a) -> dict` cùng thuật toán, đủ key theo `src/contracts.py`.
3. Đặt READY/COUNTED_READY=True khi đã triển khai; Timsort có thêm NOA_READY/NOA_COUNTED_READY.
4. Chạy test rồi nhờ reviewer kiểm tra đúng cơ chế. Không bật flag để né TODO.

```bash
python -m unittest discover -s tests -v
python -m scripts.check_ready
```

Ban đầu các test thuật toán TODO hiện SKIP và check_ready exit 1: đây là trạng thái dự kiến. Khi nghiệm thu, **không còn SKIP**, check_ready exit 0 và review cơ chế hoàn tất. Mỗi thuật toán được fuzz 1.000 ca dài 0–200; Merge/Timsort/noA test ổn định 1.000 đối tượng. Thêm test cơ chế riêng theo tests/README.md.

## 5. Chạy một cấu hình thử

```bash
python -m bench.runner --algorithm lib-sorted --dataset D1 --n 1000 --seed 2026
python -m bench.runner --algorithm lib-sorted --dataset D6 --runs 16 --n 1000 --mem
python -m bench.runner --algorithm quick --dataset D5 --k 10 --n 1000 --count
```

Lệnh quick chỉ chạy sau khi My hoàn thành. Smoke ghi `results/smoke/<run_id>/`, gồm CSV và manifest. Nó không phải dữ liệu chính thức. `--mem`/`--count` tương đương `--mode mem`/`--mode count`. Không đo cả ba trong cùng worker.

## 6. Benchmark chính thức

Hải ghi môi trường trên máy đo, điền RAM/CPU/chế độ nguồn còn thiếu và commit cùng code:

```bash
python -m scripts.capture_environment --machine-id hai-main --power-mode plugged-in-balanced
python -m scripts.check_ready
python -m unittest discover -s tests -v
```

Ví dụ power-mode chỉ là nhãn; ghi đúng chế độ thực tế của máy. Cả nhóm dùng đầy đủ cùng phiên bản CPython 3.12.x ghi trong environment.json. Benchmark chính thức kiểm tra CPython 3.12, môi trường đã ghi nhận, máy hiện tại và Git sạch. Sau khi reviewer xác nhận, commit rồi chạy:

```bash
python -m bench.runner --official --dry-run
python -m bench.runner --official --rq RQ1
python -m bench.runner --official
```

`--dry-run` chỉ liệt kê công việc, không chạy và không tạo số liệu. Lệnh cuối chạy toàn bộ RQ1–RQ3, gộp cấu hình trùng để dùng lại. Nếu đã chạy RQ1 riêng, không gộp thêm bản toàn bộ như cùng bộ lặp; dùng run_id riêng. Nếu chạy nhiều đợt, commit kết quả đợt trước trước khi mở đợt sau để Git sạch.

Dữ liệu chính thức: seed 2026/2027/2028, timeout 60 giây/lượt, N và D1–D6 theo bench/configs.json. Benchmark toàn bộ là công việc dài; không chạy toàn ma trận chỉ để kiểm tra cài đặt. Mỗi lượt lỗi vẫn được ghi trạng thái; thiếu thuật toán bị chặn trước khi khởi chạy.

## 7. Tổng hợp và vẽ hình

Thay đường dẫn RUN_ID bằng thư mục thật runner vừa in ra:

```bash
python -m bench.summarize results/raw/RUN_ID/measurements.csv --out results/summary/RUN_ID.csv
python -m pip install -r requirements-plot.txt
python -m bench.plot results/summary/RUN_ID.csv --out results/figures/RUN_ID
```

Matplotlib chỉ phục vụ hình, không import trong runner/thuật toán. Sau cài, ghi phiên bản thực tế vào môi trường hoặc requirements-plot-lock.txt (`python -m pip freeze`). Script plot ban đầu vẽ timing theo N; nhóm bổ sung hình bộ nhớ/count, sensitivity và ablation. Summary giữ khác run/máy/commit/mode riêng; không dùng lỗi để tính tốc độ. Chỉ nhóm đủ 3 seed chính thức được đánh dấu complete. Smoke muốn xem hình dùng `--include-incomplete`, chỉ dùng xem thử.

## 8. Đưa lên repo chung

Hải tạo repo rỗng tên `csd203-sorting-rbl` trên dịch vụ nhóm chọn, sau đó tại thư mục đã giải nén:

```bash
git init -b main
git add .
git commit -m "chore: initialize Sorting RBL workspace"
```

Thêm remote bằng `git remote add origin <URL_REPO_THAT>` rồi `git push -u origin main` (thay placeholder bằng URL thật, không gõ nguyên dấu ngoặc). Mời tài khoản My, Ngân, Thiện và Dân vào repo. Không có .git, remote hoặc tài khoản được giả lập trong ZIP.

Mỗi người clone repo và tạo nhánh trong PHAN_CONG.md. Dùng PR và reviewer; Hải tích hợp main. Cập nhật tiến độ bằng issue/PHAN_CONG.md, không cần họp để bắt đầu. Repo chưa có cấu hình CI phụ thuộc nhà cung cấp; lệnh test dùng giống nhau ở mọi máy.

## 9. Điều kiện hoàn thành

- Đủ thuật toán đúng đặc tả và đường đếm; không dùng thư viện thay core.
- Test/edge/fuzz/stability và review đạt; check_ready exit 0, không còn SKIP.
- Runner/môi trường được review; có CSV thật, trạng thái/checksum đúng và tái lập được.
- Có hình/bảng trả lời đủ ba RQ; nguồn và khai báo AI đã kiểm chứng.
- Paper IEEE, PDF + nguồn chỉnh sửa được, source/tests/generator/CSV/README/slide theo yêu cầu môn.

Bộ khung không điền trước số liệu, thông số laptop hoặc URL repo chưa tồn tại. D0–D14 theo lịch môn, xem docs/TIEN_DO.md. Galloping/noB được miễn cho nhóm 5 người; Powersort và noA vẫn bắt buộc.
