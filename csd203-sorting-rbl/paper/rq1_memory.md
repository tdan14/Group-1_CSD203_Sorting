# RQ1 — Bộ nhớ phụ từ thực nghiệm đã kiểm tra

Phần Ngân; Codex hỗ trợ chạy, đối chiếu và viết. Không thay xác nhận review của My.

Nguồn: `results/raw/ngan_20261029.csv`, mã nguồn `c73bc10`, generator 1.1.0, CPython 3.12.14. Môi trường và SHA-256 từng tệp ở `results/environment_ngan_20261029.json`. Máy đo thực tế là máy phát triển WIN-N3L18IBM8GL; không nhận đây là máy chính của Hải.

Mỗi ô là median [min, max] trên seed 2026/2027/2028, đơn vị byte. Bộ nhớ đo trong tiến trình riêng: tracing ngay trước sort và tắt trước oracle. Input và bản sao làm việc được chuẩn bị trước tracing. Đây là đỉnh cấp phát bổ sung, không phải RSS hoặc tổng RAM.

| N | Quick | Merge | Heap | Radix |
|---:|---:|---:|---:|---:|
| 10,000 | 1,248 [1,216, 1,280] (3/3) | 80,636 [80,636, 80,636] (3/3) | 220 [220, 220] (3/3) | 170,188 [170,188, 170,188] (3/3) |
| 50,000 | 1,440 [1,408, 1,504] (3/3) | 400,700 [400,700, 400,700] (3/3) | 220 [220, 220] (3/3) | 810,284 [810,284, 810,284] (3/3) |
| 100,000 | 1,664 [1,568, 1,664] (3/3) | 800,732 [800,732, 800,732] (3/3) | 220 [220, 220] (3/3) | 1,610,284 [1,610,284, 1,610,284] (3/3) |
| 500,000 | 1,824 [1,728, 1,888] (3/3) | 4,000,796 [4,000,796, 4,000,796] (3/3) | 220 [220, 220] (3/3) | 8,010,284 [8,010,284, 8,010,284] (3/3) |
| 1,000,000 | 1,920 [1,856, 2,112] (3/3) | 8,000,828 [8,000,828, 8,000,828] (3/3) | 220 [220, 220] (3/3) | 16,010,284 [16,010,284, 16,010,284] (3/3) |

## Diễn giải

Ở N=1.000.000, Merge có median 8,000,828 byte (7.630 MiB), tương đương 8.000828 byte/phần tử theo phép đo này. Kết quả phù hợp với một mảng phụ N tham chiếu và chi phí nhỏ hơn của biến/đệ quy. Buffer không sao chép toàn bộ đối tượng số nguyên. Không dùng byte/phần tử này như hằng số cho mọi bản Python.

Heap có median 220 byte ở N=1.000.000. O(1) bộ nhớ phụ không có nghĩa mem_peak_bytes bằng 0. Quick vẫn cần trạng thái đệ quy; tracemalloc không đo đầy đủ mọi vùng stack/native allocation.

Radix có median 16,010,284 byte ở N=1.000.000. Bản triển khai dùng output N phần tử, count 256 ô và copy-back bằng slice. Đỉnh đo bao gồm cấp phát của cách cài đặt này; không thể kết luận Radix là O(1) vì sửa trực tiếp danh sách đầu vào.

Ba seed là ba đầu vào khác nhau, không phải ba lần timing cùng một đầu vào. Min=max ở một số ô thể hiện bộ cấp phát đạt cùng đỉnh trên các lượt đã chạy; không chứng minh mọi đầu vào hoặc mọi máy đều dùng đúng số byte đó.

## Kiểm chứng và tái tạo

`python -B -m scripts.analyze_ngan --audit-only` kiểm tra ma trận, seed, nhận dạng mã/máy, SHA-256 đầu vào, checksum oracle độc lập, throughput và bộ đếm Radix. Worker đã so sánh toàn bộ đầu ra với sorted(input); checksum trong CSV không thay thế phép so sánh đó.

`python -B -m scripts.analyze_ngan` tái tạo summary CSV, phần này, bảng LaTeX và hình trong `paper/ieee/figures/`. Hình bộ nhớ RQ1 là `paper/ieee/figures/rq1_memory.pdf`; summary mọi mode ở `results/summary/ngan_20261029.csv`.
