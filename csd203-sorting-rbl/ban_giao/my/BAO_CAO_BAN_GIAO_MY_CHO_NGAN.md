# BÁO CÁO BÀN GIAO CÔNG VIỆC: MY ➔ NGÂN
**Dự án:** CSD203 Research-Based Learning — Sorting Algorithms & Timsort Study  
**Cặp phụ trách:** My & Ngân (Cặp 1 — Nhánh `rq1-my` & `rq1-ngan`)  
**Mốc thời gian:** Chuẩn bị bàn giao trước mốc D3  
**Người lập:** My

---

## PHẦN 1: TỔNG KẾT NHỮNG GÌ MY ĐÃ HOÀN THÀNH

My đã hoàn thành toàn bộ các đầu việc kỹ thuật cá nhân theo đúng đặc tả proposal và vượt tiến độ mốc D3–D4 trên nhánh `rq1-my`:

| Hạng mục | Vị trí file / module | Trạng thái | Chi tiết nghiệm thu |
|---|---|---|---|
| **Quick Sort** | [`src/quick.py`](file:///c:/Users/Admin/Desktop/CSD203/Lab/src/quick.py) | ✅ Đã hoàn thành | - Hoare partition + Median-of-Three pivot tại chỗ.<br>- Chốt pivot tại `a[mid]` đảm bảo $lo \le j < hi$, triệt tiêu nguy cơ lặp vô hạn.<br>- Không cutoff Insertion Sort, không can thiệp đệ quy.<br>- Đủ 2 giao diện: `sort(a)` và `sort_counted(a)` (đếm cả so sánh pivot). |
| **Generator D1–D3** | [`data/generate.py`](file:///c:/Users/Admin/Desktop/CSD203/Lab/data/generate.py) | ✅ Đã hoàn thành | - `D1`: Ngẫu nhiên đều $[0, 2^{31}-1]$ bằng `random.Random(seed)`.<br>- `D2`: Bằng `sorted(D1)`.<br>- `D3`: Xuất phát từ D2, hoán đổi $\lfloor N/1000 \rfloor$ cặp vị trí với luồng `seed + 10000`.<br>- Stub sẵn sàng cho D4, D5, D6 để Ngân điền tiếp. |
| **Bộ kiểm thử** | [`tests/test_quick.py`](file:///c:/Users/Admin/Desktop/CSD203/Lab/tests/test_quick.py)<br>[`tests/test_generate.py`](file:///c:/Users/Admin/Desktop/CSD203/Lab/tests/test_generate.py) | ✅ Đã hoàn thành | - Pass 100% 5 ca cố định + 1.000 ca fuzz (độ dài 0–200 phủ D1–D6) trong 0.638s.<br>- Pass 7 test kiểm tra tính tất định, miền giá trị và số lượng swap của D1–D3. |
| **Methods Quick** | [`paper/methods_quick.md`](file:///c:/Users/Admin/Desktop/CSD203/Lab/paper/methods_quick.md) | ✅ Đã hoàn thành | Bản thảo phần Phương pháp Quick Sort cho paper IEEE, trích dẫn Hoare (1962), ánh xạ từng hàm trong `src/quick.py`. |
| **Giả thuyết RQ1** | [`paper/rq1_hypothesis.md`](file:///c:/Users/Admin/Desktop/CSD203/Lab/paper/rq1_hypothesis.md) | ✅ Đã hoàn thành | Xây dựng 3 giả thuyết định lượng thời gian chạy trên D1 ($N = 10k \dots 1M$), công thức Throughput, Speedup, và hướng dẫn phân tích CSV. |
| **Nhật ký AI & Phân công** | [`PHAN_CONG.md`](file:///c:/Users/Admin/Desktop/CSD203/Lab/PHAN_CONG.md)<br>[`AI_LOG.md`](file:///c:/Users/Admin/Desktop/CSD203/Lab/AI_LOG.md) | ✅ Đã hoàn thành | Ghi nhận đầy đủ minh bạch đóng góp và các quyết định kiến trúc AI. |

---

## PHẦN 2: CHI TIẾT NHỮNG PHẦN NGÂN CẦN LÀM TIẾP THEO

Theo phân công của nhóm trong Proposal và quy ước kỹ thuật, Ngân phụ trách các đầu việc sau:

```
                    QUY TRÌNH PHỐI HỢP MY - NGÂN
  +-----------------------------------------------------------------+
  | [My]: Hoàn thành Quick Sort & Generator D1-D3 (ĐÃ XONG)         |
  +-----------------------------------------------------------------+
                                  |
                                  v
  +-----------------------------------------------------------------+
  | [Ngân - Việc 1]: Hoàn thiện Generator D4-D6 trong generate.py   |
  |  - D4: Đảo ngược D2                                             |
  |  - D5: Lấy mẫu từ K giá trị phân biệt (K = 1000, 10, 2)         |
  |  - D6: Chia D1 thành R đoạn đã sắp xếp rồi nối lại (R = 2,16,256) |
  +-----------------------------------------------------------------+
                                  |
                                  v
  +-----------------------------------------------------------------+
  | [Ngân - Việc 2]: Cài đặt Merge Sort trong src/merge.py          |
  |  - Top-down đệ quy, cấp phát duy nhất 1 mảng phụ aux cỡ N       |
  |  - Bảo đảm tính ổn định (stability) khi các khóa bằng nhau       |
  |  - Cung cấp sort(a) và sort_counted(a) theo chuẩn của nhóm      |
  +-----------------------------------------------------------------+
                                  |
                                  v
  +-----------------------------------------------------------------+
  | [Ngân - Việc 3]: Kiểm thử & Review chéo                         |
  |  - Review code Quick Sort và D1-D3 của My trên nhánh rq1-my     |
  |  - Viết test_merge.py (5 ca cố định, 1000 ca fuzz, test ổn định)|
  +-----------------------------------------------------------------+
                                  |
                                  v
  +-----------------------------------------------------------------+
  | [Ngân - Việc 4]: Viết Báo Cáo Paper IEEE                        |
  |  - Viết paper/methods_merge.md                                  |
  |  - Viết phần Bộ nhớ phụ RQ1 trong paper                         |
  |  - Tổng hợp (compile) toàn bộ bản thảo thành file hoàn chỉnh     |
  +-----------------------------------------------------------------+
```

### 1. Hoàn thiện Bộ Sinh Dữ Liệu D4–D6 (`data/generate.py`)
Mở file [`data/generate.py`](file:///c:/Users/Admin/Desktop/CSD203/Lab/data/generate.py), thay thế phần `NotImplementedError` bằng logic cụ thể theo quy ước proposal:

- **D4 (Giảm dần):**
  - Công thức: Đảo ngược dãy D2 $\rightarrow$ `list(reversed(generate("D2", n, seed)))`.
- **D5 (Nhiều giá trị trùng lặp):**
  - Tham số: $K$ giá trị phân biệt ($K = 1.000, 10, 2$).
  - Cách sinh: Dùng `random.Random(seed)` lấy mẫu không lặp $K$ giá trị trong miền $[0, 2^{31} - 1]$ làm tập khóa, sau đó chọn ngẫu nhiên $N$ phần tử từ tập đó.
- **D6 (Ghép các lô đã sắp xếp):**
  - Tham số: $R$ đoạn ($R = 2, 16, 256$).
  - Cách sinh: Chia mảng D1 ($N$ phần tử) thành $R$ đoạn liên tiếp. Nếu $N$ không chia hết cho $R$, phần dư được chia lần lượt cho các đoạn đầu (độ dài chênh nhau tối đa 1). Sắp xếp từng đoạn tăng dần bằng `sorted()` rồi nối lại thành danh sách kết quả.

### 2. Cài đặt Merge Sort (`src/merge.py`)
Ngân tạo file `src/merge.py` tuân thủ nghiêm ngặt các quy tắc:
- **Thuật toán:** Merge Sort top-down đệ quy.
- **Tối ưu bộ nhớ phụ (Rất quan trọng):** Cấp phát **duy nhất một mảng phụ `aux` kích thước $N$** ở đầu hàm `sort`/`sort_counted`, truyền mảng `aux` này qua các tầng đệ quy để tái sử dụng. **Tuyệt đối không cấp phát `a[lo:mid]` hay mảng mới ở mỗi lần merge**, vì đề bài yêu cầu kiểm soát chặt chẽ bộ nhớ phụ.
- **Bảo đảm tính ổn định (Stability):** Khi 2 phần tử bên trái và bên phải bằng nhau ($a[i] == a[j]$), **phải ưu tiên lấy phần tử bên trái trước** ($<=$) để giữ nguyên thứ tự tương đối ban đầu.
- **Giao diện chuẩn:**
  - `sort(a) -> None`: Sắp xếp tại chỗ danh sách `a`.
  - `sort_counted(a) -> dict`: Trả về đúng 5 khóa:
    ```python
    {
        "key_comparisons": int,
        "array_reads": int,
        "array_writes": int,
        "run_count": None,     # Merge Sort không áp dụng nên trả None
        "avg_run_len": None    # Trả None
    }
    ```

### 3. Bộ Kiểm Thử của Ngân (`tests/test_merge.py`)
My đã chuẩn bị sẵn bộ test review độc lập [`tests/test_merge.py`](file:///c:/Users/Admin/Desktop/CSD203/Lab/tests/test_merge.py) (hiện đang tự động skip an toàn). Khi Ngân bàn giao `src/merge.py`, Ngân chỉ cần chạy và mở rộng suite này:
1. **5 ca cố định:** `[]`, `[7]`, `[2, 1]`, `[3, 3, 3]`, `[0, 2147483647, 0]`.
2. **1.000 ca fuzz ngẫu nhiên:** Độ dài $0 \dots 200$, đối chiếu với `sorted()`.
3. **Kiểm thử tính ổn định (Stability Test):**
   - Sinh $1.000$ đối tượng chứa cặp `(key, order)`.
   - Lớp đối tượng chỉ định nghĩa toán tử `__lt__` so sánh theo `key` (không so sánh theo `order`).
   - Sắp xếp và xác nhận: với các phần tử có cùng `key`, giá trị `order` phải tăng dần nghiêm ngặt (giữ nguyên thứ tự ban đầu).

### 4. Review Chéo Phần Của My
Ngân checkout nhánh `rq1-my` để thực hiện:
- Chạy toàn bộ test của My: `python -m unittest tests.test_quick tests.test_generate -v`.
- Rà soát mã nguồn `src/quick.py` xem có tuân thủ đúng Hoare partition và Median-of-Three không.
- Ký xác nhận vào mục Reviewer trong file [`PHAN_CONG.md`](file:///c:/Users/Admin/Desktop/CSD203/Lab/PHAN_CONG.md).

### 5. Viết Báo Cáo Paper IEEE (Tối đa 6 trang)
- Soạn thảo `paper/methods_merge.md`: Trích dẫn tài liệu chuẩn, mô tả cơ chế top-down, tái sử dụng mảng phụ `aux` và chứng minh tính ổn định.
- Viết phần **Kết quả Bộ nhớ phụ RQ1**: Phân tích chi phí bộ nhớ của Merge Sort ($\mathcal{O}(N)$ do mảng `aux`) so với Quick Sort ($\mathcal{O}(1)$ ngoài call stack).
- **Tổng hợp bản thảo (Compiler):** Ngân chịu trách nhiệm ghép nối các phần văn bản của My (Quick + Thời gian RQ1), Hải (Heap + Setup), Thiện (Radix + RQ2), Dân (Timsort + RQ3) thành bản thảo hoàn chỉnh IEEE 2 cột.

---

## PHẦN 3: CÁC LỆNH CHẠY & TÀI LIỆU THAM KHẢO CHO NGÂN

1. **Lệnh chạy kiểm thử hiện tại:**
   ```bash
   python -m unittest tests.test_quick tests.test_generate -v
   ```
2. **Lệnh thử sinh dữ liệu D1–D3:**
   ```bash
   python -c "from data.generate import generate; print(generate('D1', 10, 2026))"
   ```
3. **Tài liệu tham khảo bắt buộc của đề:**
   - Hoare (1962) cho Quick Sort (đã trích dẫn trong `paper/methods_quick.md`).
   - Đề tài 1 Sorting Timsort CSD203 FA26 & Proposal nhóm 5 người.
