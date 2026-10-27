**Mục tiêu của nhóm là trả lời: dữ liệu lớn, đặc biệt dữ liệu đã có thứ tự một phần, nên được sắp xếp bằng thuật toán nào?**

Bối cảnh đề bài là xử lý dữ liệu trong AI: danh sách ID, log theo thời gian hoặc các lô dữ liệu đã được sắp xếp rồi nối lại. Nhóm phải xem xét đồng thời:

- **Thời gian:** thuật toán chạy nhanh hay chậm?
- **Bộ nhớ phụ:** cần cấp phát thêm bao nhiêu?
- **Số phép toán:** cần bao nhiêu phép so sánh hoặc lượt đọc/ghi mảng?
- **Đặc điểm đầu vào:** dữ liệu ngẫu nhiên, gần tăng dần, nhiều giá trị trùng… làm kết quả thay đổi thế nào?

Kết luận cần có điều kiện, chẳng hạn: “Trong cấu hình và loại dữ liệu đã thử, thuật toán A nhanh hơn B nhưng dùng nhiều bộ nhớ hơn”. Chưa đo thì những dự đoán như “Timsort luôn nhanh nhất” chỉ là giả thuyết.

**Ba câu hỏi nghiên cứu là khung xuyên suốt toàn bộ công việc.**

| Câu hỏi | Hiểu đơn giản | Thực nghiệm theo đề |
|---|---|---|
| **RQ1 — Khi dữ liệu lớn lên** | Bốn thuật toán cơ bản thay đổi tốc độ và bộ nhớ như thế nào? | Quick, Merge, Heap, Radix trên dữ liệu ngẫu nhiên; N = 10.000, 50.000, 100.000, 500.000, 1.000.000 |
| **RQ2 — Khi dạng dữ liệu thay đổi** | Cùng số phần tử, dữ liệu đã có thứ tự hoặc nhiều khóa trùng có làm thứ hạng thay đổi không? | Thử các họ D1–D6 ở N = 100.000 và 1.000.000, với các mức tham số được quy định |
| **RQ3 — Timsort và cơ chế bên trong** | Timsort hiệu quả ra sao so với Quick/Merge? Việc tận dụng đoạn đã có thứ tự đóng góp bao nhiêu? | Với nhóm 5 người: so sánh Quick, Merge, Timsort, Timsort `noA` và mốc thư viện `lib-sorted` |

**Ablation**, hay thí nghiệm bóc tách cơ chế, nghĩa là tạo một phiên bản tắt một kỹ thuật rồi so với phiên bản có kỹ thuật đó, giữ các điều kiện còn lại giống nhau. Ở nhóm này, trọng tâm là **bật/tắt khả năng nhận diện đoạn có thứ tự tự nhiên**.

**Phạm vi code bắt buộc gồm 4 thuật toán cơ bản và 2 phiên bản Timsort cho nhóm người.**

| Thành phần | Yêu cầu chính |
|---|---|
| **Quick Sort** | Phân hoạch Hoare; pivot là trung vị của phần tử đầu, giữa, cuối; sắp xếp tại chỗ; không chuyển sang Insertion Sort |
| **Merge Sort** | Top-down đệ quy; cấp phát một mảng phụ kích thước N và tái sử dụng; bảo đảm ổn định |
| **Heap Sort** | Max-heap tại chỗ; dựng heap từ dưới lên; không dùng `heapq` |
| **Radix Sort** | LSD, cơ số 256, đúng 4 lượt; mỗi lượt Counting Sort ổn định |
| **Timsort dùng Powersort** | Nhận diện run, tính minrun, mở rộng run ngắn bằng Binary Insertion Sort, quản lý ngăn xếp và thứ tự gộp theo Powersort |
| **Timsort `noA`** | Tắt nhận diện run tự nhiên; chia thành các khối minrun cố định, sắp xếp các khối rồi gộp |
| **`lib-sorted`** | Dùng `sorted()` để kiểm tra đáp án và làm mốc hiệu năng thư viện |

Một **run** là một đoạn liên tiếp đã có thứ tự. Ví dụ `[1, 4, 8, 2, 5, 9]` có hai đoạn tăng dễ nhận thấy: `[1, 4, 8]` và `[2, 5, 9]`. Timsort tận dụng những đoạn như vậy; Powersort quyết định thứ tự gộp chúng.

**Quyền giảm tải của nhóm này:** được bỏ cơ chế **Galloping** và không cần biến thể **`noB`**. Tuy nhiên, **Powersort, minrun, nhận diện run và `noA` vẫn nằm trong phạm vi bắt buộc**. Trong báo cáo nên nói rõ bản Timsort của nhóm áp dụng quy chế 5 người và không có Galloping.

**Dữ liệu thực nghiệm phải được sinh có kiểm soát, không chỉ nhập vài mảng mẫu.**

Miền giá trị theo đề là số nguyên từ **0 đến 2³¹ − 1**.

| Mã | Loại dữ liệu | Cách tạo |
|---|---|---|
| D1 | Ngẫu nhiên | Sinh số ngẫu nhiên với seed xác định |
| D2 | Tăng dần | Sắp xếp D1 |
| D3 | Gần tăng dần | Lấy D2 rồi hoán đổi ngẫu nhiên N/1.000 cặp |
| D4 | Giảm dần | Đảo ngược D2 |
| D5 | Nhiều giá trị trùng | Chọn phần tử từ K giá trị phân biệt; K = 1.000, 10, 2 |
| D6 | Ghép các lô đã sắp xếp | Chia D1 thành R đoạn, sắp xếp từng đoạn rồi nối lại; R = 2, 16, 256 |

Ví dụ, D6 mô phỏng việc mỗi lô log đã có thứ tự nhưng toàn bộ dữ liệu sau khi nối các lô vẫn cần sắp xếp lại. Đây là cách gắn đề tài với data pipeline mà chưa cần xây một hệ thống AI hoàn chỉnh.

**Cách triển khai nên bắt đầu từ tính đúng, sau đó mới đến đo hiệu năng.**

1. **Chốt thiết kế chung.** Thống nhất phiên bản CPython từ 3.11 trở lên, giao diện gọi các thuật toán, quy ước đầu vào/đầu ra, cách đặt tên cấu hình và các cột CSV. Viết trước giả thuyết cho từng RQ.

2. **Viết thuật toán và kiểm thử song song.** Bắt buộc có mảng rỗng, một phần tử, hai phần tử đảo thứ tự, toàn giá trị trùng và giá trị biên. Thêm **1.000 ca ngẫu nhiên**, độ dài 0–200, bao phủ D1–D6 và đối chiếu với `sorted()`.

3. **Kiểm tra tính ổn định của Merge và Timsort.** Dùng 1.000 đối tượng chứa `(key, order)`, chỉ so sánh theo `key`, rồi xác nhận các đối tượng cùng khóa giữ nguyên thứ tự ban đầu. Ví dụ hai bản ghi có cùng điểm phải giữ thứ tự tương đối sau sắp xếp.

4. **Xây bộ chạy thực nghiệm tự động.** Chương trình nhận thuật toán, loại dữ liệu, N, seed và chế độ đo; chạy rồi lưu CSV. Mỗi thuật toán phải nhận dữ liệu ban đầu tương đương, tránh việc thuật toán chạy sau nhận mảng đã được thuật toán trước sắp xếp.

5. **Chạy thử nhỏ trước, chạy ma trận chính thức sau.** Kiểm tra runner, thời gian chạy và định dạng CSV trước khi tiến hành hàng loạt cấu hình lớn.

6. **Tạo biểu đồ từ CSV và viết kết luận.** Mỗi hình phải truy được về dữ liệu đo thật; giải thích cả kết quả trái dự đoán.

Bộ đo có những quy định bắt buộc sau:

| Hạng mục | Quy định |
|---|---|
| Môi trường | CPython thống nhất; thuật toán Python thuần; không dùng NumPy, Numba, Cython… để thay phần khảo sát |
| Cách chạy | Mỗi lượt đo trong một tiến trình riêng; thuật toán bên trong chạy đơn luồng |
| Timeout | 60 giây; vượt ngưỡng ghi `timeout`, không coi là thời gian hoàn thành đúng 60 giây |
| Thời gian | Dùng `time.perf_counter_ns()`; chỉ đo thực thi thuật toán |
| Bộ nhớ | Dùng `tracemalloc` ở lượt riêng `--mem` |
| Số phép toán | Đếm ở lượt riêng `--count`; tắt bộ đếm khi đo thời gian |
| Lặp thực nghiệm | 3 lượt với 3 seed khác nhau; báo median, min, max |
| Kiểm soát | Giữ GC bật mặc định; không dùng `sys.setrecursionlimit()` để che lỗi đệ quy |

Không tính sinh dữ liệu, sao chép đầu vào chuẩn bị cho phép đo, kiểm tra đáp án, in màn hình hay ghi CSV vào thời gian thuật toán. Runner còn phải ghi trạng thái và `output_check` theo công thức checksum trong đề.

**Với 5 thành viên, cách chia phù hợp nhất với đặc tả là 2–2–1.**

| Nhóm phụ trách | Công việc kỹ thuật | Phần nghiên cứu chủ trì |
|---|---|---|
| **Thành viên 1 và 2** | Quick, Merge, bộ sinh D1–D6 và kiểm thử liên quan | RQ1 |
| **Thành viên 3 và 4** | Heap, Radix, runner và các chế độ đo | RQ2 |
| **Thành viên 5** | Timsort/Powersort, `noA`, kiểm thử ổn định | RQ3 |

Trong mỗi cặp, phải luân phiên cài đặt và kiểm thử/review. **Không chia một người chỉ code, một người chỉ viết báo cáo hoặc slide.** Các nhóm phụ trách phải review chéo và ghi đóng góp trong `PHAN_CONG.md`.

Phương án là giao phần Timsort cho người có nền tảng thuật toán vững nhất; hai cặp còn lại hỗ trợ review và kiểm thử vì đây vẫn là phần khó dù đã được giảm Galloping. Chủ trì một RQ cũng không có nghĩa chỉ dùng thuật toán do mình viết: các RQ sử dụng kết quả chung của cả nhóm.

**Lộ trình và sản phẩm nộp đã được quy định khá rõ.**

| Mốc | Kết quả cần đạt |
|---|---|
| D0–D2 | Kế hoạch nghiên cứu 1 trang, 3 RQ, giả thuyết, phân công, giao diện code chung |
| D3–D6 | Thuật toán qua kiểm thử; runner tạo được CSV mẫu; viết phần phương pháp |
| D7 | Kiểm tra tiến độ trên lớp: chạy test, demo một cấu hình, trình bày kế hoạch đo |
| D8–D10 | Hoàn thành thực nghiệm RQ1–RQ3 và thu CSV |
| D11–D12 | Sinh biểu đồ, hoàn thiện bản thảo báo cáo |
| D13 | Review chéo, kiểm tra trích dẫn, chạy lại test, đóng gói |
| D14 | Nộp và bảo vệ |

Gói nộp gồm:

- `paper/`: PDF và nguồn Word hoặc LaTeX, **IEEE hai cột, tối đa 6 trang nội dung**.
- `src/`, `tests/`: mã nguồn và bộ kiểm thử.
- `bench/`: runner và script tạo biểu đồ.
- `results/`: CSV thô và biểu đồ.
- `data/`: generator và thông tin tái tạo dữ liệu.
- `README.md`, `PHAN_CONG.md`: hướng dẫn chạy và bằng chứng đóng góp.

Báo cáo cần có bối cảnh, kiến thức nền, phương pháp, thiết lập thực nghiệm, kết quả của ba RQ, thảo luận hạn chế và kết luận. **Tiêu đề, Abstract 150–250 từ và 3–5 keywords bắt buộc bằng tiếng Anh**; tài liệu không quy định toàn bộ phần thân phải bằng tiếng Anh. Có khai báo việc dùng AI và cách nhóm kiểm chứng.

Nhóm 5 người có buổi bảo vệ **35 phút**, gồm trình bày, chạy lại cấu hình được chọn từ CSV và vấn đáp cá nhân. Thang điểm đồ án là **6 điểm nhóm + 4 điểm cá nhân**, nên mỗi người phải hiểu code, truy vết được thuật toán, sửa được yêu cầu nhỏ và giải thích số liệu. 

**Nếu muốn mở rộng một chút, phương án là chỉ chọn một hướng sau khi hoàn thành phần bắt buộc.**

| Hướng mở rộng | Giá trị bổ sung | Mức ưu tiên đề xuất |
|---|---|---|
| Thử nhiều mức xáo trộn hơn cho D3 | Thấy rõ lợi ích nhận diện run thay đổi khi dữ liệu kém có thứ tự dần | Cao |
| Tăng R của D6 thêm vài mức | Phân tích sâu ảnh hưởng số lô và độ dài run | Cao |
| Tăng N lên 2 triệu | Bổ sung bằng chứng về khả năng mở rộng; đề đã cho phép nếu đủ thời gian | Vừa |
| Bổ sung Galloping và `noB` | Đo thêm đóng góp của cơ chế thứ hai | Khó, chỉ nên làm khi phần chính đã chắc |
| Làm minh họa từng bước trên mảng nhỏ | Hỗ trợ thuyết trình và luyện vấn đáp | Phụ trợ |

Với nhóm này, cần ưu tiên **làm chắc Timsort/Powersort, runner và số liệu của ba RQ**, rồi mở rộng độ xáo trộn của D3. Hướng này bám sát câu hỏi nghiên cứu và tận dụng được phần lớn code đã có. Một chương trình dòng lệnh rõ ràng là đủ để triển khai; giao diện chỉ nên làm sau khi các phần được chấm chính đã hoàn chỉnh.
