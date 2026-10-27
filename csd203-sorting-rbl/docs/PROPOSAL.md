# Phần II Proposal nghiên cứu và phân công

## Kế hoạch nghiên cứu tóm tắt

**Đề tài:** Khảo sát thực nghiệm các thuật toán sắp xếp kinh điển và Timsort dùng Powersort trên dữ liệu gần có thứ tự của pipeline AI.

**Nhóm:** My, Ngân, Hải, Thiện và Dân. Mục tiêu là xác định điều kiện lựa chọn thuật toán theo thời gian, bộ nhớ phụ và số phép toán trong môi trường Python thuần. Đây là nghiên cứu thực nghiệm; các nhận định dưới đây là giả thuyết cần kiểm chứng bằng dữ liệu.

| RQ và người phụ trách | Phạm vi thực nghiệm | Giả thuyết ban đầu |
|---|---|---|
| RQ1 — My và Ngân | Quick, Merge, Heap, Radix trên D1; 5 mức N từ 10.000 đến 1.000.000 | Các cài đặt có tốc độ tăng thời gian và chi phí bộ nhớ khác nhau; Radix với 4 lượt cố định có thể có xu hướng tăng trưởng thuận lợi. |
| RQ2 — Hải và Thiện | Bốn thuật toán cơ bản trên D1–D6, N = 100.000 và 1.000.000; đủ các mức K và R | Mức có thứ tự, số khóa phân biệt và cấu trúc lô có thể làm thay đổi thứ hạng hiệu năng. |
| RQ3 — Dân | Quick, Merge, Timsort, noA và lib-sorted trên cùng dữ liệu D1–D6, ở hai mức N trên | Nhận diện run có lợi rõ hơn trên dữ liệu có các run dài; lợi ích có thể giảm hoặc không xuất hiện trên dữ liệu ngẫu nhiên. |

**Phạm vi:** Cài đặt Python thuần; Timsort có Powersort, minrun và nhận diện run. Áp dụng giảm tải nhóm 5 người: bỏ Galloping và noB. Chưa triển khai GUI hoặc mở rộng trong giai đoạn bắt buộc.

**Phương pháp:** Một máy đo chính, CPython 3.12, ba seed 2026/2027/2028; tách thời gian, bộ nhớ và bộ đếm; mỗi lượt là một tiến trình riêng với timeout 60 giây. Kiểm tra đúng bằng oracle; lưu CSV gốc và báo median/min/max.

**Đầu ra và mốc:** D2 chốt giao diện và kế hoạch; D6 thuật toán qua test và runner hoạt động; D7 demo tiến độ; D10 đủ CSV; D12 có bản thảo; D13 kiểm tra tái lập; D14 nộp và bảo vệ. Gói nộp gồm paper IEEE tối đa 6 trang nội dung, source, tests, generator, runner, CSV, biểu đồ, README, phân công, khai báo AI và slide.

**Tổ chức:** My–Ngân phụ trách Quick/Merge và generator; Hải–Thiện phụ trách Heap/Radix và runner; Dân phụ trách Timsort/noA. Hải tích hợp và vận hành benchmark; Ngân tổng hợp bản thảo. Mỗi người viết và bảo vệ phần kỹ thuật của mình.


**Tài liệu căn cứ:** csd203_sorting_rbl_nhom_5_nguoi(1).md; Quy định chung đồ án nhóm CSD203 FA26; Đề tài 1 Sorting Timsort CSD203 FA26. Khi viết phần thuật toán, đọc các nguồn bắt buộc trong đặc tả: Hoare (1962), Williams (1964), listsort.txt của CPython, Munro và Wild (2018), Goodrich và cộng sự (2013). Mỗi cơ chế Timsort/Powersort cần ánh xạ tới hàm triển khai trong Methods.


## Phân công cá nhân và phối hợp

Các phân công và quy ước từ phần này là kế hoạch triển khai của nhóm. Các yêu cầu bắt buộc của môn và phạm vi giảm tải được giữ như Phần I. Thành viên bắt đầu theo bảng nhiệm vụ; mọi điều chỉnh được ghi trong PHAN_CONG.md, không cần tổ chức họp để khởi động.

| Thành viên | Triển khai chính | Kiểm thử và review | Phần báo cáo và bàn giao |
|---|---|---|---|
| My | Quick Sort; generator D1–D3 | Test/review Merge và D4–D6; review Heap | Phương pháp Quick; biểu đồ thời gian và phân tích RQ1 |
| Ngân | Merge Sort; generator D4–D6 | Test/review Quick và D1–D3; review Radix | Phương pháp Merge; bộ nhớ RQ1; tổng hợp bản thảo |
| Hải | Heap Sort; runner, worker và đo thời gian | Test/review Radix và chế độ mem/count; review ngăn xếp Powersort | Thiết lập thực nghiệm; tích hợp code; chạy benchmark chính |
| Thiện | Radix Sort; chế độ mem/count và xuất CSV | Test/review Heap, timing và timeout; review run, noA và stability | Phương pháp Radix; biểu đồ và phân tích RQ2 |
| Dân | Timsort/Powersort, noA; bộ test ổn định | Review chéo Quick/Merge; kiểm tra đối chứng RQ3 | Phương pháp Timsort; biểu đồ, ablation và phân tích RQ3 |

Trong mỗi cặp, mỗi người vừa triển khai vừa kiểm thử phần của người còn lại. Ngân phối hợp với Dân áp dụng test ổn định cho Merge. Hải và Thiện review hai phần của Timsort để Dân không phải tự xác nhận toàn bộ cài đặt. Mỗi tác giả sửa lỗi do reviewer phát hiện và bổ sung test hồi quy trước khi ghép.

**Phụ thuộc bàn giao:** My–Ngân cung cấp generator chung trước D3; Hải cung cấp khung gọi thuật toán và CSV mẫu trước D3. Đến D4, mỗi thành viên ghép ít nhất một thuật toán đã qua test nhỏ vào runner. RQ1 sử dụng cả Heap/Radix; RQ3 sử dụng Quick/Merge. Người chủ trì RQ không viết lại thuật toán đã có.

**Quản lý mã nguồn:** Hải khởi tạo một Git repository tên csd203-sorting-rbl. Nhánh làm việc lần lượt là rq1-my, rq1-ngan, rq2-hai, rq2-thien và rq3-dan; main chỉ nhận thay đổi đã qua test và review. Hải thực hiện tích hợp. URL repository được Hải ghi trong README khi tạo; đây là thao tác triển khai, không phải nội dung chờ quyết định.

**Lưu đóng góp:** PHAN_CONG.md ghi người triển khai, người review, module, commit, test và kết quả liên quan. Mỗi người cập nhật ngắn tiến độ và vướng mắc sau phiên làm việc. Khi thay đổi giao diện, Hải cập nhật đặc tả và báo cho các chủ module trước khi ghép. AI Log ghi các gợi ý quan trọng, quyết định chấp nhận/sửa/bác bỏ và bằng chứng kiểm chứng.


## Giao diện mã nguồn và môi trường

**Môi trường:** Chọn CPython 3.12, môi trường ảo venv và unittest cho kiểm thử. Hải ghi đầy đủ phiên bản 3.12.x trên máy đo vào README trước D2; các thành viên cài cùng bản đó. Thuật toán, generator và runner dùng thư viện chuẩn. Matplotlib chỉ dùng ở script tạo hình từ CSV, nằm ngoài phép đo và được ghi phiên bản trong requirements-plot.txt.

**Máy đo:** Phân công máy của Hải làm máy đo chính. Hải ghi CPU, RAM, hệ điều hành, phiên bản Python và chế độ nguồn vào environment.json. Nếu máy không khả dụng, chuyển toàn bộ lượt đo chính thức sang máy Thiện và ghi thay đổi; không trộn hai máy trong một bảng so sánh. Không điền thông số phần cứng khi chưa kiểm tra thực tế.

**Giao diện chuẩn:** Mỗi module cung cấp sort(a) → None, sắp xếp tăng dần trực tiếp danh sách a. Hàm sort không kiểm tra miền đầu vào, không ghi log, không ghi CSV và không bật bộ đếm. Việc xác thực đầu vào do runner/test thực hiện bên ngoài vùng đo. Merge và Timsort được dùng bộ nhớ phụ đúng đặc tả dù cùng giao diện sửa danh sách tại chỗ.

**Lượt đếm:** Mỗi module cung cấp sort_counted(a) → dict với cùng kết quả sắp xếp, trả về key_comparisons, array_reads, array_writes, run_count và avg_run_len. Trường không áp dụng trả None. Hai đường chạy phải có cùng quyết định thuật toán và qua test đối chiếu; không chèn cập nhật bộ đếm vào sort(a).

**Tính ổn định:** Merge/Timsort nhận được các đối tượng so sánh chỉ theo key. Dùng __lt__ theo key và giữ order để kiểm chứng, không sắp xếp tuple theo cả hai trường. Khi khóa bằng nhau phải giữ thứ tự ban đầu. Radix chỉ nhận số nguyên trong miền quy định.

| Vị trí | Nội dung và chủ trách nhiệm |
|---|---|
| src/quick.py và src/merge.py | Quick — My; Merge — Ngân |
| src/heap.py và src/radix.py | Heap — Hải; Radix — Thiện |
| src/timsort.py | Timsort và noA, dùng chung phần minrun/merge/Powersort — Dân |
| data/generate.py | generate(dataset, n, seed, k=None, runs=None) → list[int] — My, Ngân |
| bench/runner.py và bench/worker.py | Điều phối tiến trình, gọi thuật toán và chế độ đo — Hải, Thiện |
| bench/configs.json và bench/plot.py | Ma trận thử và biểu đồ — Hải quản lý cấu hình; từng RQ bổ sung hình |
| tests/ và results/ | Test theo module; results/raw và results/figures theo run_id |
| paper/ và tài liệu gốc repository | Paper, slide, README, PHAN_CONG.md, AI_LOG.md, environment.json |

**Tên thuật toán trong CSV:** quick, merge, heap, radix, timsort, timsort-noA, lib-sorted. timsort là bản nhóm 5 người không Galloping; timsort-noA chỉ tắt nhận diện run, giữ các cơ chế còn lại. lib-sorted gọi sorted(a) và nhận danh sách trả về, không sao chép kết quả trở lại a trong vùng đo.


## Dữ liệu và ma trận thực nghiệm

**Seed chính thức:** 2026, 2027, 2028. Mỗi cấu hình và chế độ đo chạy một lượt cho mỗi seed, tổng cộng ba lượt. Fuzz test dùng seed riêng 203 để không nhầm với bộ benchmark. Mỗi phép so sánh giữa thuật toán dùng cùng dữ liệu đầu vào và cùng phiên bản generator.

**Quy ước generator:** D1 dùng random.Random(seed), miền [0, 2³¹ − 1]. D2 là sorted(D1); D4 đảo D2. D3 xuất phát từ D2, thực hiện floor(N/1000) lần hoán đổi hai vị trí phân biệt, có thể lặp vị trí giữa các lần; dùng luồng random.Random(seed + 10000) cho việc chọn vị trí. Với N nhỏ hơn 1000, số lần hoán đổi bằng 0. D5 lấy K giá trị phân biệt bằng lấy mẫu không lặp trong miền, rồi chọn ngẫu nhiên N phần tử từ tập đó. D6 chia D1 thành R đoạn liên tiếp; phần dư chia lần lượt cho các đoạn đầu, độ dài chênh nhau tối đa 1; sắp từng đoạn rồi nối lại. R là số lô sinh ra, không mặc nhiên bằng số run tự nhiên Timsort nhận diện.

**Định danh dữ liệu:** Lưu dataset, N, K, R, seed, generator_version và input_sha256. Checksum đầu vào là SHA-256 của dãy số được mã hóa unsigned 32-bit little-endian theo đúng thứ tự. Checksum tính ngoài vùng đo. Dữ liệu lớn được tái tạo từ generator và cấu hình; lưu mẫu nhỏ để minh họa.

| RQ | Thuật toán | Quy mô và dữ liệu |
|---|---|---|
| RQ1 | quick, merge, heap, radix | D1; N = 10.000, 50.000, 100.000, 500.000, 1.000.000 |
| RQ2 | quick, merge, heap, radix | N = 100.000 và 1.000.000; D1–D4; D5 với K = 1.000, 10, 2; D6 với R = 2, 16, 256 |
| RQ3 | quick, merge, timsort, timsort-noA, lib-sorted | Cùng 2 mức N và 10 cấu hình dữ liệu như RQ2 |

Hải gộp các cấu hình trùng nhau để chạy một lần và dùng lại kết quả cho các RQ liên quan. Ba chế độ là time, mem và count; lib-sorted chỉ đo time/mem vì không thể đếm các phép toán nội bộ bằng cùng cơ chế Python thuần. Các trường count của lib-sorted để trống, không ghi 0.

**Giao thức lượt đo:** Worker sinh dữ liệu và bản sao làm việc trước khi đo, làm nóng một lần trên dữ liệu cùng họ với N tối đa 1.000 rồi bỏ kết quả. GC giữ bật mặc định. Chế độ time chỉ bao quanh lời gọi thuật toán bằng perf_counter_ns. Chế độ mem dùng tiến trình riêng, chỉ bật tracemalloc ngay trước thuật toán và đọc đỉnh cấp phát trước khi tắt. Chế độ count chạy riêng. Mọi lượt đều kiểm tra kết quả ngoài vùng đo.

Hải chạy tuần tự bằng subprocess.run với timeout=60. Không chạy benchmark đồng thời với các tác vụ nặng khác. Thời gian khởi động, generator, warm-up, oracle và CSV không được cộng vào elapsed_ms. Timeout áp dụng toàn tiến trình; ghi thêm phase để phân biệt chưa đến vùng thuật toán với đang sắp xếp. Không dùng một timeout ở khâu chuẩn bị để kết luận thuật toán cần hơn 60 giây.


## Kết quả kiểm thử và tiêu chí nghiệm thu

**Schema CSV:** Một dòng cho một thuật toán × dữ liệu × seed × chế độ × phiên bản code. Hải và Thiện thống nhất thứ tự cột như bảng dưới; cột không áp dụng để trống. CSV dùng UTF-8, dấu phẩy phân cách và dấu chấm thập phân.

| Nhóm trường | Tên cột |
|---|---|
| Định danh và môi trường | run_id, rq, algorithm, code_commit, generator_version, machine_id, python_version |
| Đầu vào và chế độ | dataset, n, k, runs, seed, input_sha256, mode |
| Trạng thái và xác thực | status, phase, error_type, output_check, oracle_match |
| Kết quả đo | elapsed_ms, throughput_kps, mem_peak_bytes, key_comparisons, array_reads, array_writes, run_count, avg_run_len |

**Trạng thái:** ok khi kết quả trùng đầy đủ với oracle; wrong khi sai; timeout khi worker bị ngắt quá hạn; oom khi xác định được lỗi bộ nhớ; crash cho lỗi khác, kể cả RecursionError. Không tự suy đoán oom từ mọi trường hợp tiến trình bị dừng. Dòng không hoàn thành hoặc sai không được dùng tính tốc độ; giữ lại dòng và nguyên nhân để phân tích.

**Kiểm tra đáp án:** So sánh đầy đủ danh sách kết quả với sorted của đầu vào. Đồng thời tính output_check bằng h = (31 × h + x) mod 2⁶⁴, bắt đầu h = 0. Checksum hỗ trợ truy vết; không thay thế phép so sánh đáp án đầy đủ. Chế độ mem tắt tracing trước khi tạo/kiểm tra oracle để không tính bộ nhớ kiểm thử.

**Bộ test bắt buộc:** Mọi thuật toán và noA qua [], [7], [2, 1], [3, 3, 3], [0, 2147483647, 0] và 1.000 ca ngẫu nhiên độ dài 0–200 bao phủ D1–D6. Với D6 nhỏ cho phép lô rỗng. Merge, Timsort và noA qua kiểm thử ổn định trên 1.000 bản ghi. Thêm test ranh giới minrun, run giảm ngặt, khóa bằng nhau và các lần gộp nhiều run. sort và sort_counted phải cho cùng đầu ra.

**Quy ước đếm:** Quick/Merge/Heap/Timsort đếm từng phép so sánh khóa thực tế, gồm chọn pivot và xử lý run nếu có. Radix đếm đọc/ghi phần tử trong mảng dữ liệu, mảng tạm và mảng đếm; không tính thao tác của runner/oracle. Báo riêng loại chỉ số, không đặt số đọc/ghi của Radix ngang số so sánh như cùng một đơn vị. run_count/avg_run_len thu ở lượt count; ghi rõ run là run tự nhiên trước mở rộng minrun. Với noA các trường natural-run để trống.

**Tổng hợp:** Với elapsed_ms > 0, throughput_kps = N / elapsed_ms. Báo median/min/max và số lượt ok trên ba seed, không gộp khác máy hoặc commit. Khi có lượt lỗi, nêu số lượt thành công; không trình bày median của tập thiếu như đủ ba lượt. Speedup = thời gian baseline / thời gian phương án so sánh. Mức giảm thời gian do nhận diện run = (T_noA − T_timsort) / T_noA × 100%; giá trị âm là kết quả hợp lệ.

RQ3 đối chứng timsort/noA trên cùng điều kiện. Khoảng cách với lib-sorted chỉ là mốc thư viện, không quy toàn bộ lợi ích cho Powersort hay nhận diện run vì khác môi trường thực thi mã. Báo cáo giải thích kết quả trái giả thuyết và giới hạn suy rộng.


## Tiến độ thực hiện và bàn giao

D0 là mốc bắt đầu được áp dụng theo lịch giao đề của môn; các mốc dưới đây dùng ngày tương đối D0–D14. Hải ghi ngày lịch tương ứng vào PHAN_CONG.md khi khởi tạo repository. Kế hoạch không tự thay đổi hạn nộp hoặc lịch kiểm tra của giảng viên.

| Mốc | Người chủ trì | Bàn giao và điều kiện hoàn thành |
|---|---|---|
| D0–D2 | Hải; cả nhóm | Repository, môi trường, giao diện, CSV mẫu, 3 RQ và giả thuyết; mỗi người có nhiệm vụ và reviewer |
| D3–D4 | My, Ngân; Hải, Thiện; Dân | Generator dùng chung; mỗi module ghép được vào runner; test nhỏ đúng; bản Methods đầu tiên |
| D5–D6 | Từng chủ module | Đủ thuật toán, noA và test bắt buộc; ba chế độ đo hoạt động; cấu hình pilot tạo CSV hợp lệ |
| D7 | Hải demo; cả nhóm trả lời | Demo test, runner một cấu hình và kế hoạch đo; chuẩn bị theo checkpoint 10 phút của môn |
| D8–D10 | Hải vận hành; chủ RQ kiểm tra | Đủ CSV cho ba RQ; rà soát checksum, lỗi và kết quả bất thường; chưa chạy mở rộng nếu còn thiếu phần bắt buộc |
| D11–D12 | My, Ngân, Thiện, Dân | Biểu đồ từ CSV; mỗi RQ có kết luận có điều kiện; Ngân ghép paper, Hải hoàn thiện Setup |
| D13 | Cả nhóm | Review chéo báo cáo và trích dẫn; hồi quy test; chạy lại cấu hình chọn từ CSV; gói nộp đủ thành phần |
| D14 | Cả nhóm | Nộp và bảo vệ theo lịch môn; mỗi người giải thích, trace, sửa code và diễn giải số liệu phần mình |

**Phân công viết:** My viết Quick và kết quả thời gian RQ1; Ngân viết Merge, bộ nhớ RQ1 và ghép bản thảo; Hải viết Heap và Experimental Setup; Thiện viết Radix và RQ2; Dân viết Timsort, ablation và RQ3. Mỗi người bổ sung hạn chế liên quan phần mình. Ngân tổng hợp Introduction/Conclusion từ kết quả đã kiểm chứng; cả nhóm review.

**Điều kiện nghiệm thu gói nộp:** Code chạy theo README; test đạt; mỗi hình truy được về CSV và script; mỗi kết luận định lượng có cấu hình và baseline; không có số liệu giả. Có PDF và nguồn paper, source/tests, generator, dữ liệu mẫu, CSV gốc, script vẽ, môi trường, PHAN_CONG.md, AI_LOG.md và slide. Bản paper tuân thủ yêu cầu IEEE của môn; tài liệu bối cảnh và kế hoạch này không bị áp dụng giới hạn 6 trang của paper.

**Kiểm tra tái lập trước bảo vệ:** Hải chạy lại một số dòng đã nộp trên máy đo chính. status và output_check phải khớp; thời gian trong biên độ 0,5–2,0 lần median theo quy định môn. Khi có chênh lệch, kiểm tra môi trường và chạy lại có ghi log; không xóa số liệu bất lợi. Cả nhóm luyện vấn đáp cá nhân không dùng AI.

**Xử lý vướng mắc:** Lỗi tính đúng ưu tiên sửa trước đo; lỗi generator hoặc phần đo dùng chung yêu cầu chạy lại cấu hình bị ảnh hưởng. Timeout/crash/oom được lưu đúng trạng thái, không đổi thuật toán bắt buộc hoặc tăng giới hạn đệ quy để che lỗi. Nếu module chậm bàn giao, reviewer hỗ trợ test và tích hợp; tác giả vẫn chịu trách nhiệm hiểu và bảo vệ phần đó.

**Mở rộng sau nghiệm thu:** Chỉ khi đủ ba RQ, bổ sung D3 với số hoán đổi floor(N/10000), floor(N/1000), floor(N/100) tại N = 100.000, giữ nguyên seed và thuật toán. Ghi nhãn extension, không thay D3 chuẩn trong kết quả bắt buộc. Không triển khai Galloping/noB trong kế hoạch cơ sở.
