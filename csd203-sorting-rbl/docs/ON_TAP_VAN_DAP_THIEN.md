# TÀI LIỆU ÔN TẬP VẤN ĐÁP CÁ NHÂN (D14) — THÀNH VIÊN: THIỆN

**Môn học:** CSD203 Data Structures and Algorithms  
**Mục tiêu:** Nắm chắc 100% bản chất thuật toán Radix Sort LSD và phân tích RQ2, tự tin trace code trên bảng và trả lời trọn vẹn 4/4 điểm vấn đáp cá nhân độc lập (không sử dụng AI).

---

## PHẦN 1: BÀI TRACE THUẬT TOÁN TỪNG BƯỚC (DÙNG ĐỂ VẼ LÊN BẢNG TRONG 3 PHÚT)

### 📌 VÍ DỤ TRACE: Mảng nhỏ $a = [170, 45, 75, 90, 802, 24, 2, 66]$
*Thuật toán:* LSD Radix Sort, cơ số $b = 256$ (xử lý trên từng byte 8-bit).  
*Miền giá trị:* Số nguyên 32-bit không âm $[0, 2^{31} - 1]$. Cố định đúng **4 lượt** ($shift \in \{0, 8, 16, 24\}$).

#### 1. Lượt 0 (Byte 0: bit 0–7, `shift = 0`)
- **Trích xuất byte:** `byte_val = (x >> 0) & 0xFF`
  - $170 = \text{0xAA} \rightarrow 170$
  - $45 = \text{0x2D} \rightarrow 45$
  - $75 = \text{0x4B} \rightarrow 75$
  - $90 = \text{0x5A} \rightarrow 90$
  - $802 = 3 \times 256 + 34 = \text{0x0322} \rightarrow 34$
  - $24 = \text{0x18} \rightarrow 24$
  - $2 = \text{0x02} \rightarrow 2$
  - $66 = \text{0x42} \rightarrow 66$
- **Xây dựng mảng đếm `count[256]` & Cộng dồn (Prefix Sums):**
  - Các bucket nhận giá trị: `count[2]=1`, `count[24]=1`, `count[34]=1`, `count[45]=1`, `count[66]=1`, `count[75]=1`, `count[90]=1`, `count[170]=1`.
  - Prefix sum: Xác định vị trí kết thúc của từng bucket.
- **Duyệt ngược từ $n-1$ về 0 và ghi vào `output`:**
  - $x = 66 \rightarrow byte=66 \rightarrow pos = count[66]-1 \rightarrow output[pos] = 66$
  - ...
  - **Mảng sau Lượt 0:** `[2, 24, 802, 45, 66, 75, 90, 170]`

#### 2. Lượt 1 (Byte 1: bit 8–15, `shift = 8`)
- **Trích xuất byte:** `byte_val = (x >> 8) & 0xFF`
  - Với các số nhỏ $< 256$: byte 1 đều bằng 0.
  - Số $802 = 3 \times 256 + 34 \rightarrow byte = 3$.
- **Duyệt ngược bảo toàn thứ tự:**
  - Tất cả các số có byte 1 bằng 0 giữ nguyên thứ tự tương đối đã đạt được ở Lượt 0: `[2, 24, 45, 66, 75, 90, 170]`.
  - Số 802 có byte 1 bằng 3 được đặt vào bucket 3 (phía sau bucket 0).
  - **Mảng sau Lượt 1:** `[2, 24, 45, 66, 75, 90, 170, 802]` (Đã sắp xếp xong!).

#### 3. Lượt 2 & 3 (Byte 2 & Byte 3: `shift = 16, 24`)
- Vì tất cả các số trong ví dụ đều $< 2^{16}$, byte 2 và 3 đều bằng 0.
- Thuật toán vẫn quét đủ 2 lượt này để tuân thủ đặc tả đề bài (đúng 4 lượt cố định), mảng giữ nguyên thứ tự đã sắp xếp hoàn hảo.
- **Kết quả cuối cùng:** `[2, 24, 45, 66, 75, 90, 170, 802]`.

---

## PHẦN 2: CÁC CÂU HỎI VẤN ĐÁP CỐT LÕI (GIẢNG VIÊN THƯỜNG HỎI)

### Câu 1: Tại sao nhóm chọn cơ số $b = 256$ mà không phải cơ số 10 hay 16?
- **Trả lời:**
  1. Số trong máy tính được lưu trữ dưới dạng nhị phân. $256 = 2^8$, tương ứng chính xác với 1 byte dữ liệu.
  2. Việc trích xuất chữ số được thực hiện bằng toán tử dịch bit (`>>`) và phép AND bitwise (`& 0xFF`). Đây là phép toán ở mức CPU instruction, nhanh hơn rất nhiều so với phép chia nguyên (`// 10`) và lấy dư (`% 10`) của cơ số 10.
  3. Với số nguyên 32-bit ($[0, 2^{31}-1]$), cơ số 256 chỉ cần đúng $d = 32 / 8 = 4$ lượt lặp. Kích thước mảng đếm $b = 256$ rất nhỏ, nằm trọn vẹn trong L1 Data Cache của CPU, tối ưu hóa triệt để bộ nhớ đệm.

### Câu 2: Tại sao Counting Sort trong Radix Sort BẮT BUỘC phải duyệt ngược từ $n-1$ về $0$?
- **Trả lời:**
  - Để đảm bảo **tính ổn định (Stability)**.
  - Sau bước tính tổng cộng dồn (prefix sums), `count[k]` trỏ đến vị trí *cuối cùng* của các phần tử có khóa $k$.
  - Khi ta duyệt từ phải sang trái (từ $n-1$ về 0), phần tử nào đứng sau trong mảng ban đầu sẽ được ghi vào vị trí sau trong mảng `output`. Do đó, các phần tử có cùng giá trị byte sẽ giữ nguyên thứ tự tương đối trước đó. Nếu duyệt xuôi từ 0 đến $n-1$, thứ tự tương đối sẽ bị đảo ngược và thuật toán LSD sẽ cho kết quả sai hoàn toàn!

### Câu 3: Tại sao trong `sort_counted`, nhóm gán `key_comparisons = None`?
- **Trả lời:**
  - Radix Sort là thuật toán sắp xếp **không dựa trên so sánh** (Non-comparison sort). Nó phân loại phần tử vào các bucket dựa trên giá trị số học của từng byte, không thực hiện bất kỳ phép so sánh cặp phần tử nào ($a[i] < a[j]$).
  - Đề bài quy định rõ: không được gán `0` hay tính số lần đọc/ghi mảng ngang hàng với phép so sánh khóa, vì vậy trả về `None` là tuyệt đối chính xác theo quy ước khoa học.

### Câu 4: Phản hồi về chênh lệch $4N$ lần đọc giữa `sort` và `sort_counted` (Ngân review)?
- **Trả lời:**
  - Trong bản ban đầu, hàm `sort(a)` viết: `count[byte_val] -= 1; output[count[byte_val]] = val` $\rightarrow$ đọc `count[byte_val]` 2 lần.
  - Bản `sort_counted(a)` dùng: `pos = count[byte_val] - 1; count[byte_val] = pos; output[pos] = val` $\rightarrow$ chỉ đọc `count[byte_val]` 1 lần.
  - Thiện đã đồng nhất hoàn toàn: đưa biến `pos` vào cả hàm `sort(a)`. Nhờ vậy, hai hàm có chung 100% quyết định và số lần truy cập mảng, đồng thời giúp hàm `sort(a)` loại bỏ $4N$ lần truy cập mảng thừa trong CPython bytecode, tăng tốc độ thực thi.

### Câu 5: Kết quả RQ2 cho thấy điều gì về Radix Sort so với Quick, Merge, Heap?
- **Trả lời:**
  1. **Tính bất biến phân phối (Distribution Invariance):** Thời gian của Radix Sort gần như không đổi trên cả 6 phân phối D1–D6 vì luôn thực hiện đúng 4 lượt Counting Sort, độ phức tạp $O(4(N + 256))$.
  2. **Đánh đổi Không gian - Thời gian (Space-Time Trade-off):**
     - Heap Sort chạy tại chỗ ($S(N) = 0$), nhưng chậm gấp 2.5 lần do nhảy con trỏ cache miss.
     - Radix Sort nhanh vượt trội trên mảng lớn, nhưng tốn mảng đệm phụ kích thước $N$ (khoảng $O(N)$ bộ nhớ).

---

## PHẦN 3: TÌNH HUỐNG SỬA CODE TẠI CHỖ (LIVE CODING TEST)

### Tình huống 1: Giảng viên yêu cầu sắp xếp GIẢM DẦN bằng Radix Sort
- **Cách sửa:**
  Chỉ cần sửa bước tính Prefix Sum (cộng dồn từ 254 lùi về 0 thay vì từ 1 tiến đến 255):
  ```python
  # Sắp xếp tăng dần (Gốc)
  for j in range(1, 256):
      count[j] += count[j - 1]

  # Sửa thành giảm dần:
  for j in range(254, -1, -1):
      count[j] += count[j + 1]
  ```

### Tình huống 2: Giảng viên yêu cầu đổi cơ số sang 16 (4-bit, 8 lượt lặp)
- **Cách sửa:**
  ```python
  # Đổi shifts thành 8 bước cách nhau 4 bit:
  for shift in range(0, 32, 4):  # 0, 4, 8, 12, 16, 20, 24, 28
      count = [0] * 16           # 16 buckets
      for x in a:
          count[(x >> shift) & 0x0F] += 1
      for j in range(1, 16):
          count[j] += count[j - 1]
      for idx in range(n - 1, -1, -1):
          val = a[idx]
          pos = count[(val >> shift) & 0x0F] - 1
          count[(val >> shift) & 0x0F] = pos
          output[pos] = val
      a[:] = output
  ```
