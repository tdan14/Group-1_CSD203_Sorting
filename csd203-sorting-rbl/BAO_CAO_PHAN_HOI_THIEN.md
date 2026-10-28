# BÁO CÁO PHẢN HỒI REVIEW & ĐÓNG GÓP TÍCH HỢP — THIỆN (`rq2-thien`)

> **Người gửi:** Thiện (`rq2-thien`)  
> **Người nhận:** Cả nhóm (My, Ngân, Hải, Dân)  
> **Thời điểm:** 28/10/2026  
> **Căn cứ:** Tài liệu đề bài CSD203 FA26, báo cáo tích hợp `docs/TICH_HOP.md`, `BAO_CAO_SUA_DOI.md` của Hải và `ban_giao/ngan/PHAN_CONG.md`.

---

## 1. Phản hồi góp ý của Ngân về bộ đếm Radix Sort

- **Vấn đề Ngân nêu:** Bản `sort(a)` thực hiện `count[byte_val] -= 1` rồi đọc lại `count[byte_val]` trong `output[count[byte_val]] = val`. Trong khi bản `sort_counted(a)` dùng biến `pos`, dẫn đến lệch $4N$ lần đọc mảng.
- **Xử lý của Thiện:** 
  - Đã cập nhật lại cả `src/radix.py` và `ban_giao_hai/src/radix.py`.
  - Cả hai hàm `sort(a)` và `sort_counted(a)` hiện nay **hoàn toàn đồng nhất 100%**: đều dùng biến `pos = count[byte_val] - 1; count[byte_val] = pos; output[pos] = val`.
  - **Kết quả:** Loại bỏ hoàn toàn $4N$ lần đọc thừa trong CPython bytecode, giúp hàm chạy nhanh hơn và khớp chính xác 100% với số lần đọc/ghi được đếm trong `sort_counted`.
  - Đã chạy lại toàn bộ unit tests: **100% PASS** (2/2 test methods, bao gồm 1.000 ca fuzzing và toàn bộ ca biên).

---

## 2. Xác nhận Review cho Hải (`src/heap.py` & Runner/Ma trận)

- **Về thuật toán Heap Sort:**
  - Đã kiểm tra `src/heap.py`: Dựng max-heap bottom-up từ $\lfloor N/2 \rfloor - 1$ về 0 theo đúng đặc tả Williams (1964), không dùng `heapq`.
  - Đánh giá cao việc áp dụng kỹ thuật *hole sift-down* (chỉ gán giá trị ở bước cuối) giúp giảm số lần ghi mảng.
  - Giao diện `sort(a)` và `sort_counted(a)` chuẩn đặc tả, trả về đúng `key_comparisons`, `array_reads`, `array_writes`.
- **Về Generator & Runner:**
  - Xác nhận sửa đổi D3 trong `data/generate.py` v1.1.0 dùng `swap_rng.sample(range(n), 2)` đảm bảo 2 vị trí luôn phân biệt.
  - Xác nhận ma trận `bench/configs.json` mới 1.308 lượt (gộp chung cả RQ1, RQ2, RQ3).
  - Xác nhận cơ chế ghi nhận `phase` khi timeout và cờ `--resume`.
- **Kiểm thử trên máy dự phòng:**
  - Đã chạy kiểm tra toàn bộ test suite trên máy đo dự phòng của Thiện: **72/72 test đạt**.

---

## 3. Xác nhận Review cho Dân (`src/timsort.py` & Tính ổn định)

- Đã kiểm tra `src/timsort.py`:
  - Cơ chế tìm natural run (cho phép cả strictly decreasing rồi đảo ngược).
  - Mở rộng minrun bằng binary insertion sort và tính minrun chuẩn trong khoảng $[32, 64]$.
  - Gộp run theo chính sách Powersort (node powers).
  - Bản `timsort-noA` tắt natural run và chia đều theo minrun cố định.
  - Vượt qua kiểm thử tính ổn định trên 1.000 bản ghi `(key, order)`.

---

## 4. Gửi Ngân các file phục vụ ghép Paper IEEE

Thiện bàn giao đầy đủ các nội dung để Ngân ghép vào bài báo 6 trang:
1. [`paper/methods_radix.md`](paper/methods_radix.md): Phần Phương pháp cho Radix Sort (tiếng Anh), phân tích độ phức tạp thời gian $\Theta(4(N + 256))$, bộ nhớ phụ $\Theta(N + 256)$ và trích dẫn Goodrich et al. (2013).
2. [`paper/rq2_hypothesis.md`](paper/rq2_hypothesis.md): Phần giả thuyết và kế hoạch phân tích cho RQ2 (cùng Hải).
3. [`paper/rq2_analysis.md`](paper/rq2_analysis.md): Phần Kết quả & Thảo luận sơ bộ cho RQ2 (sẽ cập nhật số liệu chính thức khi Hải chạy xong ma trận).

---

## 5. Cập nhật nhật ký đóng góp vào `PHAN_CONG.md`

Đề nghị Dân/Ngân bổ sung dòng sau vào bảng nhật ký đóng góp chung của repo:

| Ngày | Người | Module và thay đổi | Commit/PR | Reviewer | Test/CSV/bằng chứng |
|---|---|---|---|---|---|
| 2026-10-28 | Thiện (`rq2-thien`) | Đồng nhất biến `pos` trong `src/radix.py` (sửa lệch 4N lượt đọc theo góp ý của Ngân); review Heap của Hải và Timsort của Dân; nộp methods_radix.md và rq2_hypothesis.md | `rq2-thien` | Ngân, Hải | 72/72 test PASS; test_radix PASS 1.000 fuzz cases; BAO_CAO_PHAN_HOI_THIEN.md |
