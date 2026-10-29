# Nhật ký hỗ trợ AI

## Phần Ngân và bản thảo có thực nghiệm — 29–30/10/2026

- Người yêu cầu: Ngân. Công cụ: Codex; người dùng yêu cầu chạy thật, bổ sung
  bằng chứng thiếu và cập nhật GitHub, không tạo số liệu theo kỳ vọng.
- Giữ nguyên `src/`, `data/`, `bench/` tại commit `c73bc10`. Thực thi toàn
  bộ config trên máy phát triển đã ghi ở manifest, tách time/mem/count.
  Dữ liệu gốc: `results/raw/ngan_20261029.csv`; không dùng dữ liệu mẫu hay
  các số của bản nháp RQ2 không có CSV nguồn.
- Bổ sung test quan sát Quick/Radix; test chống thiếu/trùng/sửa dữ liệu cho
  trình audit. Audit tái sinh đầu vào và tính checksum bằng biểu thức độc
  lập, kiểm tra toàn bộ cấu hình, source hash, oracle, mode và đơn vị.
- Tạo phân tích bộ nhớ RQ1, thay phân tích RQ2 bằng số đo, tổng hợp bài IEEE
  tại `paper/ieee/main.tex`. Bảng/hình và summary sinh bằng
  `scripts/analyze_ngan.py`, không gõ tay các giá trị đo vào bài.
- Đối chiếu nguồn sơ cấp Hoare, Williams, Merge.java, Munro–Wild và CPython
  listsort; đối chiếu ví dụ companion Goodrich về bản ghi so sánh theo key.
  Không nhận đã đọc toàn bộ sách. Sửa giả thuyết và diễn giải khi trái dữ
  liệu; không coi mục tiêu điểm số là điều kiện để chọn kết quả thuận lợi.
- Giới hạn: thứ tự chạy cố định, ba seed khác nhau, tải nền/nhiệt độ không
  kiểm soát hoàn toàn; không phải lần đo chính thức trên máy Hải. Tác giả
  phải đọc, hiểu và review bài trước khi nộp. AI không ký thay reviewer.

## Tích hợp và phần Dân — 28/10/2026

- Công cụ: Codex, theo yêu cầu Dân.
- Ràng buộc: không cải thiện, sửa hoặc thêm/bớt logic của My, Ngân, Hải,
  Thiện. Giữ nguyên bản bàn giao và tài liệu riêng; chỉ nối giao diện
  của bộ khung với source đã nhận.
- Thực hiện: giữ 97 file gốc, ghép nguyên nội dung 27 file vào vị trí
  chung, thêm manifest SHA-256 và công cụ đối chiếu. Không sửa các vấn
  đề Radix/runner đã được nêu; ghi lại để nhóm xử lý sau.
- Phần mới: Timsort/Powersort/noA, counted, 8 test riêng và tài liệu phần
  Dân. Code dùng vòng lặp/hàm tường minh, không lambda hay comprehension.
  Tham khảo mô tả Powersort và mã CPython 3.12; link trong Methods.
- Kiểm chứng: 72 test chung đạt, không skip, trên CPython 3.12.13.
  Tính ổn định, buffer ngắn, power và trình tự so sánh có kiểm tra riêng.
  Kết quả kiểm tra worker ở `docs/TICH_HOP.md`.
- Dân chưa tự review trong phiên này. Không nhận đây là code Dân đã tự
  viết hoặc nhóm đã nghiệm thu. Chưa chạy ma trận nghiên cứu chính thức.
- AI log cũ của My và Ngân giữ nguyên trong `ban_giao/my/AI_LOG.md` và
  `ban_giao/ngan/AI_LOG.md`. Thư mục Hải/Thiện giữ các tài liệu họ gửi.

## Khởi tạo bộ khung

- Công cụ: ChatGPT/Codex theo yêu cầu của Dân.
- Phạm vi: README, phân công, hợp đồng module, generator, registry, runner/worker, config, checksum, test khung, summary, script hình và tài liệu cộng tác.
- Thuật toán khảo sát: chưa triển khai; các module giữ TODO/NotImplementedError.
- Kiểm chứng của nhóm: chưa thực hiện tại thời điểm tạo bộ khung. Chủ module bổ sung test/review/commit khi bàn giao.
- Chạy smoke bằng lib-sorted chỉ kiểm tra hạ tầng, không phải kết quả nghiên cứu.

## Quyết định tiếp theo

| Ngày | Người | AI gợi ý | Chấp nhận/sửa/bác bỏ và lý do | Commit/test/CSV |
|---|---|---|---|---|
| 2026-10-29 | Thiện (`rq2-thien`) | Đồng nhất biến `pos` trong `src/radix.py` (loại bỏ 4N lượt đọc mảng theo góp ý Ngân); nộp methods_radix.md, rq2_hypothesis.md, rq2_analysis.md; review Heap và Timsort | Chấp nhận: sửa triệt để độ lệch số lượt đọc mảng, đảm bảo 2 hàm đồng nhất 100% | 72/72 test đạt trên CPython 3.12 |

Kiểm chứng phần Ngân: 80/80 test đạt trên CPython 3.12.14; check_ready đạt.
Ma trận mới có 1.308 lượt, tất cả status=ok. Manifest bàn giao lịch sử
khớp 96/97: bản Radix trong ban_giao/thien đã được sửa ở 4faec1c trước
đợt này; không phải sửa đổi mới của Ngân.

Audit hoàn tất: 1.308/1.308 lượt ok; 436/436 nhóm đủ ba seed; 69 đầu vào
được tái sinh và đối chiếu hash/checksum. Chạy lại riêng Merge/D1/N=100.000/
seed=2026/mem: oracle đúng, input/output checksum khớp và peak 800.732 byte
khớp dòng gốc. Lượt replay không được chèn vào CSV nghiên cứu.
