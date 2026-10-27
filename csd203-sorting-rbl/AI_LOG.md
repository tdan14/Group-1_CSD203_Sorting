# Nhật ký hỗ trợ AI

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
