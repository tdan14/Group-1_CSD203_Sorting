# Nhật Ký Tương Tác và Sử Dụng AI (AI_LOG.md)

**Môn học:** CSD203 Data Structures and Algorithms — Research-Based Learning  
**Thành viên:** My  
**Vai trò:** Cài đặt Quick Sort, Generator D1–D3, Kiểm thử, Phương pháp Quick Sort, Phân tích RQ1  
**Mục đích:** Ghi nhận minh bạch các gợi ý kiến trúc từ AI, quyết định chấp nhận / sửa đổi / bác bỏ của nhóm, và bằng chứng kiểm chứng bằng kiểm thử thực tế theo quy định liêm chính học thuật.

---

## Bảng Tổng Hợp Các Quyết Định Thiết Kế

| STT | Vấn đề / Gợi ý từ AI | Quyết định | Lý do kỹ thuật | Bằng chứng kiểm chứng |
|---|---|---|---|---|
| 1 | **Kiến trúc hàm Quick Sort:** Thiết kế chung 1 hàm đệ quy lõi `_quick(a, lo, hi, cnt)` dùng cờ/dictionary `cnt` cho cả `sort` và `sort_counted`, thay vì viết 2 hàm độc lập. | **Chấp nhận (Accept)** | Tránh phân kỳ thuật toán (logic divergence), đảm bảo `sort` và `sort_counted` luôn ra cùng một quyết định chọn pivot và phân hoạch. | Unit test `QuickFixed` và 1.000 ca `QuickFuzz` xác nhận `arr_sort == arr_counted` trên 100% các trường hợp. |
| 2 | **Vị trí Pivot Median-of-Three:** Đổi pivot về đầu mảng (`a[lo]`) hoặc cuối mảng (`a[hi]`) sau khi tính median. | **Sửa đổi (Modify)** | Giữ pivot trực tiếp tại vị trí `a[mid]` sau khi sắp xếp $a[lo] \le a[mid] \le a[hi]$. Với phân hoạch Hoare, việc chốt pivot ở $mid$ bảo đảm $j < hi$ và $j \ge lo$, triệt tiêu hoàn toàn nguy cơ lặp vô hạn (infinite recursion). | Chạy thành công ca biên hiểm hóc `[0, 2147483647, 0]`, ca toàn khóa trùng `[3, 3, 3]`, và 1.000 ca fuzz trong 0.638s mà không bị tràn stack hay timeout. |
| 3 | **Tối ưu Small Subarray Cutoff:** Tự động chuyển sang Insertion Sort khi kích thước mảng con $N \le 16$ để cải thiện hằng số thời gian. | **Bác bỏ (Reject)** | Đề bài quy định nghiêm ngặt: *"Sắp xếp tại chỗ và không chuyển sang Insertion Sort khi mảng nhỏ"*. Việc tự ý thêm cutoff sẽ làm sai lệch đối tượng nghiên cứu thuần túy của Quick Sort. | Kiểm tra mã nguồn bằng AST/reflection xác nhận không có module `insertion` hay logic cutoff nào trong `src/quick.py`. |
| 4 | **Quy ước đếm `key_comparisons`:** Chỉ đếm các phép so sánh trong vòng lặp phân hoạch, bỏ qua các so sánh lúc chọn pivot. | **Bác bỏ (Reject)** | Đề bài quy định: *"key_comparisons phải đếm từng phép so sánh khóa thực tế, kể cả các phép so sánh khi chọn pivot"*. Median-of-three thực hiện đúng 3 phép so sánh khóa khi $hi - lo \ge 2$ và 1 phép khi $hi - lo = 1$. | `tests/test_quick.py` kiểm tra số `key_comparisons` luôn phản ánh cả phép so sánh median-of-three và so sánh partition. |
| 5 | **Không tăng recursion limit:** Không dùng `sys.setrecursionlimit()` để che giấu lỗi đệ quy. | **Chấp nhận (Accept)** | Quy định bắt buộc: nếu đệ quy vượt ngưỡng mặc định của Python, lỗi phải được ghi nhận là `crash` trong thực nghiệm. Nhờ median-of-three và Hoare, độ sâu ngăn xếp trên D1 được kiểm soát ở mức xấp xỉ $\mathcal{O}(\log N)$. | Kiểm tra mã nguồn `assert 'recursionlimit' not in inspect.getsource(src.quick)` đạt kết quả sạch. |
| 6 | **Luồng ngẫu nhiên D3:** D3 sử dụng luồng `random.Random(seed + 10000)` để chọn cặp vị trí hoán đổi trên nền D2. | **Chấp nhận (Accept)** | Tách biệt luồng sinh dữ liệu ban đầu và luồng xáo trộn, bảo đảm dữ liệu D3 có tính tất định và có thể tái tạo độc lập. | `tests/test_generate.py` xác nhận tính tất định 100% trên các seed 2026, 2027, 2028 và fuzz seed 203. |
| 7 | **Dùng matplotlib cho script vẽ biểu đồ RQ1:** Sử dụng thư viện ngoài stdlib (matplotlib) để vẽ biểu đồ từ file CSV kết quả. | **Chấp nhận (Accept)** | Quy định proposal dòng 417 cho phép dùng thư viện ngoài ở script tạo hình từ CSV, nằm hoàn toàn ngoài vùng đo benchmark của thuật toán. | Đã pin phiên bản trong `requirements-plot.txt`; `bench/plot_rq1.py` không chạy benchmark, không import thuật toán, không ảnh hưởng tính thuần túy stdlib ở các module đo. |
