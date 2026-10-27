# TÀI LIỆU ÔN TẬP VẤN ĐÁP CÁ NHÂN (D14) — THÀNH VIÊN: MY

**Môn học:** CSD203 Data Structures and Algorithms  
**Mục tiêu:** Nắm chắc 100% bản chất thuật toán, trace code trên bảng và trả lời trọn vẹn 4/4 điểm vấn đáp cá nhân độc lập (không sử dụng AI).

---

## PHẦN 1: BÀI TRACE THUẬT TOÁN TỪNG BƯỚC (DÙNG ĐỂ VẼ LÊN BẢNG TRONG 3 PHÚT)

### 📌 TRACE 1: Mảng ngẫu nhiên `a = [5, 1, 6, 2, 10, 3]`
Đoạn ban đầu: `lo = 0, hi = 5, mid = (0 + 5) // 2 = 2`.

#### Bước 1: Chọn Pivot Median-of-Three (`_median_of_three`)
Ba vị trí xét: `a[0] = 5`, `a[2] = 6`, `a[5] = 3`.
1. So sánh `a[0] > a[2]` ($5 > 6 \rightarrow \text{False}$): Giữ nguyên.
2. So sánh `a[2] > a[5]` ($6 > 3 \rightarrow \text{True}$): Hoán đổi $a[2] \leftrightarrow a[5]$.  
   $\rightarrow$ Mảng thành: `[5, 1, 3, 2, 10, 6]`.
3. So sánh `a[0] > a[2]` ($5 > 3 \rightarrow \text{True}$): Hoán đổi $a[0] \leftrightarrow a[2]$.  
   $\rightarrow$ Mảng thành: `[3, 1, 5, 2, 10, 6]`.
- **Kết quả:** $a[0] \le a[2] \le a[5]$ ($3 \le 5 \le 6$).
- **Chốt Pivot:** $\text{pivot} = a[\text{mid}] = a[2] = \mathbf{5}$.

#### Bước 2: Phân hoạch Hoare (`_hoare_partition`)
Khởi tạo: $i = -1, j = 6, \text{pivot} = 5$.

| Vòng lặp | Con trỏ $i$ tiến (dừng khi $a[i] \ge 5$) | Con trỏ $j$ lùi (dừng khi $a[j] \le 5$) | Điều kiện & Hoán đổi | Trạng thái mảng sau bước |
|---|---|---|---|---|
| **Vòng 1** | $i = 0$ ($3 < 5$)<br>$i = 1$ ($1 < 5$)<br>$i = 2$ ($5 < 5 \rightarrow \text{Dừng!}$) | $j = 5$ ($6 > 5$)<br>$j = 4$ ($10 > 5$)<br>$j = 3$ ($2 > 5 \rightarrow \text{Dừng!}$) | $i < j$ ($2 < 3$)<br>$\rightarrow \text{Swap } a[2] \leftrightarrow a[3]$ | `[3, 1, 2, 5, 10, 6]` |
| **Vòng 2** | $i = 3$ ($5 < 5 \rightarrow \text{Dừng!}$) | $j = 2$ ($2 > 5 \rightarrow \text{Dừng!}$) | $i \ge j$ ($3 \ge 2$)<br>$\rightarrow \mathbf{Break!}$ | Trả về chỉ số cắt: $\mathbf{j = 2}$ |

#### Bước 3: Đệ quy hai nửa
- **Nửa trái:** $a[0 \dots 2] = [3, 1, 2] \rightarrow$ sắp xếp thành $[1, 2, 3]$.
- **Nửa phải:** $a[3 \dots 5] = [5, 10, 6] \rightarrow$ sắp xếp thành $[5, 6, 10]$.
- **Mảng sắp xếp hoàn chỉnh:** `[1, 2, 3, 5, 6, 10]`.

---

### 📌 TRACE 2: Ca biên toàn phần tử trùng `a = [3, 3, 3]`
Đoạn: `lo = 0, hi = 2, mid = 1`.
1. **Median-of-Three:** Ba phần tử $a[0]=3, a[1]=3, a[2]=3$. Thực hiện đúng 3 phép so sánh $>$, không hoán đổi. Chốt $\text{pivot} = a[1] = \mathbf{3}$.
2. **Hoare Partition:**
   - $i$ tăng lên 0: $a[0] < 3$ là False $\rightarrow$ dừng tại $i = 0$.
   - $j$ giảm xuống 2: $a[2] > 3$ là False $\rightarrow$ dừng tại $j = 2$.
   - $i < j$ ($0 < 2$): Hoán đổi $a[0] \leftrightarrow a[2]$ (hai giá trị 3 đổi cho nhau).
   - Vòng tiếp theo: $i$ tăng lên 1 ($a[1] < 3$ False) dừng tại $i = 1$; $j$ giảm xuống 1 ($a[1] > 3$ False) dừng tại $j = 1$.
   - $i \ge j$ ($1 \ge 1$): Dừng và trả về $\mathbf{j = 1}$.
3. **Đệ quy:** Tách thành $a[0 \dots 1] = [3, 3]$ và $a[2 \dots 2] = [3]$. Phân hoạch chia đều ngay giữa mảng, **chứng minh thuật toán không bao giờ lặp vô hạn trên mảng trùng**.

---

## PHẦN 2: CHỨNG MINH TOÁN HỌC KHÔNG LẶP VÔ HẠN (1 TRANG)

**Mệnh đề:** Với phân hoạch Hoare kết hợp Median-of-Three chốt pivot tại $a[\text{mid}]$, hàm phân hoạch luôn trả về chỉ số $j$ thỏa mãn $\text{lo} \le j < \text{hi}$.

**Chứng minh:**
1. Sau hàm `_median_of_three`, ta có bất đẳng thức: $a[\text{lo}] \le \text{pivot} \le a[\text{hi}]$ với $\text{pivot} = a[\text{mid}]$.
2. **Chặn dưới của $j$:** Do $a[\text{lo}] \le \text{pivot}$, điều kiện dừng của con trỏ $j$ ($a[j] \le \text{pivot}$) chắc chắn được thỏa mãn ít nhất tại vị trí $\text{lo}$. Do đó, $j$ không bao giờ giảm xuống dưới $\text{lo}$, suy ra $j \ge \text{lo}$.
3. **Chặn trên của $j$:** Con trỏ $i$ bắt đầu từ $\text{lo}-1$. Do $\text{mid} = \lfloor(\text{lo}+\text{hi})/2\rfloor < \text{hi}$ khi $\text{lo} < \text{hi}$ và $a[\text{mid}] = \text{pivot}$, con trỏ $i$ sẽ dừng trễ nhất tại vị trí $\text{mid} < \text{hi}$. Vì $i < \text{hi}$, tại lần hoán đổi cuối cùng hoặc điều kiện dừng, $j$ bắt buộc phải thỏa mãn $j < \text{hi}$.
4. **Kết luận kích thước đệ quy:**
   - Phân vùng trái: $a[\text{lo} \dots j]$ có kích thước $(j - \text{lo} + 1) \le (\text{hi} - 1 - \text{lo} + 1) < (\text{hi} - \text{lo} + 1)$.
   - Phân vùng phải: $a[j + 1 \dots \text{hi}]$ có kích thước $(\text{hi} - j) \le (\text{hi} - \text{lo}) < (\text{hi} - \text{lo} + 1)$.
   Cả hai mảng con đều **giảm kích thước nghiêm ngặt** qua từng bước đệ quy. Thuật toán luôn hội tụ về bài toán cơ sở ($\text{lo} \ge \text{hi}$) mà không cần cutoff và không bao giờ lặp vô hạn. $\blacksquare$

---

## PHẦN 3: BỘ 10 CÂU HỎI VẤN ĐÁP THƯỜNG GẶP & CÂU TRẢ LỜI CHUẨN

#### 1. Vì sao chốt pivot tại `a[mid]` chứ không đổi về `a[lo]` hay `a[hi]`?
*Trả lời:* Trong phân hoạch Hoare, nếu đưa pivot về `a[hi]`, khi mảng đã sắp xếp, con trỏ $j$ có thể dừng ngay tại `hi`, dẫn đến $j = \text{hi}$. Khi đó nửa trái giữ nguyên $N$ phần tử còn nửa phải rỗng, gây lặp vô hạn (Infinite Recursion). Giữ pivot tại `a[mid]` đảm bảo toán học $j < \text{hi}$ trên mọi trường hợp. *(Tham chiếu: [`src/quick.py`](file:///c:/Users/Admin/Desktop/CSD203/Lab/src/quick.py#L34-L83))*

#### 2. Quick Sort của nhóm chạy trên dữ liệu D2 (tăng dần) hoặc D4 (giảm dần) có bị $\mathcal{O}(N^2)$ không?
*Trả lời:* Hoàn toàn không. Với mảng tăng hoặc giảm dần, 3 phần tử đầu, giữa, cuối luôn có một phần tử nằm chính xác ở khoảng trung vị thực sự của mảng. Median-of-Three sẽ chọn đúng phần tử này làm pivot, chia mảng thành hai nửa bằng nhau, giúp Quick Sort đạt hiệu năng tối ưu $\mathcal{O}(N \log N)$.

#### 3. Vì sao đề cấm chuyển sang Insertion Sort khi mảng nhỏ, và điều này ảnh hưởng gì?
*Trả lời:* Đề tài nhằm nghiên cứu hành vi tiệm cận thuần túy của Quick Sort trên toàn bộ các dải kích thước. Không có cutoff, các mảng con kích thước nhỏ ($\le 16$) vẫn phải chịu chi phí overhead gọi hàm đệ quy và 3 phép so sánh của MOT, khiến hằng số thời gian tổng thể của Python cao hơn bản có cutoff. *(Tham chiếu: `AI_LOG.md` Mục #3 & `paper/limitations_quick.md`)*

#### 4. Tại sao Generator D3 lại dùng luồng `seed + 10000` riêng cho vị trí hoán đổi?
*Trả lời:* Để tách biệt hoàn toàn luồng sinh dữ liệu nền ban đầu (D1/D2 dùng `seed`) và luồng xáo trộn vị trí. Điều này đảm bảo tính tất định và khả năng tái lập độc lập của thực nghiệm: thay đổi cách xáo trộn không làm biến đổi các giá trị số nguyên ban đầu. *(Tham chiếu: [`data/generate.py`](file:///c:/Users/Admin/Desktop/CSD203/Lab/data/generate.py#L39-L55))*

#### 5. Với $N < 1000$, dữ liệu D3 có gì đặc biệt và test nào chứng minh?
*Trả lời:* Công thức quy định số lần hoán đổi là $\lfloor N/1000 \rfloor$. Khi $N < 1000$, số lần hoán đổi bằng $0$, do đó $D3$ giống hệt $D2$ (mảng tăng dần $100\%$). Điều này đã được chứng minh trong `tests/test_generate.py` hàm `test_d3_swap_count_and_behavior` với $N = 500$.

#### 6. Fuzz test dùng seed 203 khác 3 seed chính thức (2026, 2027, 2028) nhằm mục đích gì?
*Trả lời:* Nhằm đảm bảo tính khách quan và liêm chính học thuật. Dữ liệu kiểm thử hồi quy và fuzz test không được trùng với dữ liệu đo benchmark chính thức, tránh nguy cơ thuật toán bị "overfitting" hoặc điều chỉnh logic phục vụ riêng cho các seed đo.

#### 7. Công thức tính `throughput_kps` là gì? Vì sao báo `median` thay vì trung bình (mean)?
*Trả lời:* $\text{throughput\_kps} = N / \text{elapsed\_ms}$ (kilo-phần tử/giây). Nhóm báo `median` trên 3 seed vì trong môi trường hệ điều hành đa nhiệm, thời gian thực thi có thể xuất hiện đột biến (outlier) do tác vụ nền hoặc garbage collector; median phản ánh xu hướng trung tâm chính xác hơn mean.

#### 8. Nếu có 1 seed bị lỗi (timeout hoặc crash), báo cáo kết quả như thế nào?
*Trả lời:* Theo quy ước proposal, phải báo cáo rõ số lượt thành công dạng "2/3 ok", và chỉ tính median/min/max trên 2 lượt thành công đó. Tuyệt đối không được trình bày số liệu của 2 lượt như thể là của đủ 3 lượt, và không được tự ý xóa dòng lỗi để giấu số liệu bất lợi.

#### 9. Vì sao quy định nghiêm cấm gộp số liệu khác `machine_id` hoặc khác `code_commit`?
*Trả lời:* Mỗi máy tính có kiến trúc CPU, bộ nhớ đệm L1/L2/L3 và xung nhịp khác nhau; mỗi commit có thể chứa thay đổi mã nguồn. Gộp lẫn lộn sẽ làm sai lệch bản chất khoa học của thực nghiệm. Script `bench/plot_rq1.py` đã cài đặt cơ chế tự động cô lập theo `(machine_id, code_commit)` chiếm đa số.

#### 10. Giả thuyết RQ1 dự đoán Quick Sort nhanh hơn Merge Sort trên Python thuần vì sao?
*Trả lời:* Quick Sort sắp xếp tại chỗ (in-place) với phân hoạch Hoare quét 2 con trỏ, duy trì tính cục bộ bộ nhớ đệm (spatial cache locality) rất tốt và số lần ghi mảng ít. Ngược lại, Merge Sort trong Python phải copy phần tử ra mảng phụ `aux` kích thước $N$, làm tăng đáng kể chi phí cấp phát và giải phóng tham chiếu đối tượng trong CPython.

#### 11. Bộ test fuzz của My kiểm thử phủ cả D1–D6, nhưng lúc đó Ngân chưa bàn giao D4–D6 thì My lấy dữ liệu ở đâu để fuzz?
*Trả lời:* Trong `tests/test_quick.py`, My đã tự xây dựng hàm helper `_generate_mock_d4_to_d6` mô phỏng chính xác hành vi đặc tả của D4 (đảo D2), D5 (mẫu K giá trị phân biệt), D6 (chia R lô đã sắp xếp) độc lập với Ngân. Thiết kế này tuân thủ nguyên tắc cách ly module (module decoupling): giúp bộ kiểm thử của Quick Sort có thể chạy và phát hiện lỗi ngay từ D3 mà không bị phong tỏa (block) bởi tiến độ của thành viên khác. Sau này `tests/test_merge.py` cũng tái sử dụng hàm mock này.
