# RQ2 — Phân tích từ ma trận đo thực tế

Chủ RQ2: Hải và Thiện. Ngân tổng hợp với hỗ trợ Codex sau khi chạy và audit. Bản này thay bản nháp dẫn rq2_pilot.csv không có trong repo; không sử dụng các số của bảng cũ.

Nguồn: `results/raw/ngan_20261029.csv`, commit `c73bc10`, CPython 3.12.14, generator 1.1.0, máy phát triển WIN-N3L18IBM8GL. Seed 2026/2027/2028; time/mem/count chạy riêng. Chi tiết mọi mode, min/max và n_ok nằm ở `results/summary/ngan_20261029.csv`. Mọi kết luận dưới đây chỉ áp dụng các bản triển khai và môi trường đã đo.

## Thời gian ở N = 100,000

Đơn vị ms, mỗi ô median [min, max] từ ba seed thành công. Nếu thiếu lượt thành công, ô sẽ ghi n_ok/3 và không dùng để xếp hạng.

| Dữ liệu | Quick | Merge | Heap | Radix |
|---|---:|---:|---:|---:|
| D1 | 326.13 [315.75, 336.64] | 250.10 [223.68, 281.48] | 291.78 [241.82, 361.28] | 107.65 [97.50, 120.36] |
| D2 | 190.74 [190.74, 200.49] | 200.14 [199.85, 201.48] | 211.22 [210.11, 218.41] | 103.65 [92.62, 172.34] |
| D3 | 206.23 [191.23, 226.00] | 209.94 [209.39, 210.59] | 212.76 [210.65, 213.24] | 126.93 [125.08, 162.91] |
| D4 | 206.25 [203.92, 210.82] | 207.05 [200.74, 215.43] | 198.52 [195.85, 222.21] | 121.60 [100.18, 154.60] |
| D5 K=1000 | 312.44 [305.87, 314.16] | 214.26 [209.44, 214.59] | 197.12 [195.33, 198.20] | 70.36 [69.56, 95.91] |
| D5 K=10 | 334.62 [332.37, 336.51] | 208.96 [208.26, 212.68] | 175.23 [171.91, 178.41] | 70.59 [68.59, 70.98] |
| D5 K=2 | 340.21 [339.14, 353.31] | 193.94 [193.19, 198.95] | 98.65 [97.47, 100.40] | 67.98 [67.77, 84.16] |
| D6 R=2 | 662.74 [482.01, 744.55] | 210.61 [209.62, 213.52] | 202.52 [201.93, 210.88] | 120.17 [114.62, 146.44] |
| D6 R=16 | 368.07 [352.56, 520.30] | 204.20 [203.62, 212.34] | 208.35 [202.50, 214.33] | 171.06 [155.45, 188.46] |
| D6 R=256 | 341.22 [307.21, 449.15] | 224.08 [223.71, 224.13] | 211.40 [206.71, 212.20] | 159.40 [139.10, 174.47] |

Median thời gian Radix giữa các phân phối nằm trong khoảng 67.98–171.06 ms. Median cấp phát phụ của Heap là 220–220 byte, Radix 1,609,548–1,610,284 byte. Khoảng này mô tả các median giữa phân phối, không phải khoảng tin cậy.

## Thời gian ở N = 1,000,000

Đơn vị ms, mỗi ô median [min, max] từ ba seed thành công. Nếu thiếu lượt thành công, ô sẽ ghi n_ok/3 và không dùng để xếp hạng.

| Dữ liệu | Quick | Merge | Heap | Radix |
|---|---:|---:|---:|---:|
| D1 | 4454.79 [3974.24, 5201.59] | 3783.97 [3486.38, 5158.84] | 4790.74 [4224.70, 4899.99] | 1760.36 [1753.39, 1775.93] |
| D2 | 2874.41 [2728.51, 2937.79] | 3331.86 [3156.07, 3416.08] | 2850.62 [2836.12, 2872.36] | 2117.03 [2037.43, 2386.12] |
| D3 | 2659.78 [2619.94, 2818.79] | 3325.42 [3256.23, 3389.82] | 2878.11 [2873.35, 2916.13] | 2034.24 [2028.04, 2077.33] |
| D4 | 2783.76 [2759.83, 2811.26] | 3430.82 [3410.05, 3543.51] | 2869.66 [2863.60, 2921.31] | 2092.69 [2006.23, 2152.36] |
| D5 K=1000 | 3822.33 [3637.67, 3832.50] | 2525.27 [2484.64, 2531.93] | 2774.19 [2730.45, 2977.08] | 728.08 [720.14, 759.42] |
| D5 K=10 | 3872.30 [3825.57, 3935.27] | 2405.35 [2402.32, 2498.69] | 2215.71 [2200.51, 2219.20] | 675.89 [667.29, 688.39] |
| D5 K=2 | 3973.54 [3970.92, 3992.38] | 2359.70 [2304.32, 2407.77] | 1221.46 [1197.36, 1248.78] | 695.26 [686.02, 704.47] |
| D6 R=2 | 8760.56 [8036.73, 9117.82] | 3115.26 [3057.91, 3194.07] | 3015.49 [3006.28, 3062.25] | 2096.34 [1936.53, 2110.91] |
| D6 R=16 | 4262.94 [4185.88, 4309.03] | 2932.16 [2923.27, 2954.24] | 4837.60 [4005.88, 5293.88] | 2358.75 [1877.05, 2857.95] |
| D6 R=256 | 3918.54 [3906.57, 3928.81] | 3067.78 [2959.63, 3076.12] | 4561.92 [4446.31, 4627.65] | 1952.50 [1779.50, 2115.78] |

Median thời gian Radix giữa các phân phối nằm trong khoảng 675.89–2358.75 ms. Median cấp phát phụ của Heap là 220–220 byte, Radix 16,009,164–16,010,284 byte. Khoảng này mô tả các median giữa phân phối, không phải khoảng tin cậy.

## Bộ đếm và kết luận có điều kiện

Với N >= 2, code Radix hiện tại đếm reads = 20N + 2040 và writes = 17N + 2044. N=100.000 cho 2.002.040 lần đọc và 1.702.044 lần ghi; N=1.000.000 cho 20.002.040 lần đọc và 17.002.044 lần ghi. Trình audit kiểm tra mọi dòng Radix count; test độc lập quan sát đường sort bình thường để đối chiếu, gồm buffer và copy-back. Đây là truy cập phần tử logic, không phải số truy cập RAM hoặc mọi thao tác nội bộ CPython.

Số lượt quét cố định không làm thời gian bất biến. D5 có thể giảm thời gian thực tế dù số truy cập logic Radix không đổi. Không quy kết nhân quả cho cache hay entropy khi chưa đo trực tiếp các cơ chế đó. Heap có bộ nhớ phụ O(1), không phải 0 byte. Radix dùng buffer N phần tử nên có bộ nhớ phụ O(N). Việc sửa danh sách đầu vào không thay đổi kết luận này.

Không có cơ sở từ thí nghiệm này để tuyên bố thuật toán tối ưu cho mọi pipeline AI hoặc hệ nhúng. Dữ liệu là mô phỏng đặc điểm thứ tự; không đo hệ thống AI đầu cuối. Dòng lib-sorted thuộc ma trận RQ3, không được tự thêm vào RQ2 như đã có trong thiết kế 720 lượt.

Tái tạo: `python -B -m scripts.analyze_ngan`; kiểm tra độc lập không vẽ: `python -B -m scripts.analyze_ngan --audit-only`. Hình so sánh ở `paper/ieee/figures/rq2_relative_time.pdf`; paper tổng hợp ở `paper/ieee/main.tex`.
