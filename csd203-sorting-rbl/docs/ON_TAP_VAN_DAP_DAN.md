# Ôn tập phần Dân

Đọc cùng `src/timsort.py`, tự chạy và trace lại các ví dụ dưới đây.

## Từ hàm gọi đến phần xử lý

`sort(a)` gọi `_sort(a, True)`. `sort_noa(a)` gọi `_sort(a, False)`.
Cả hai sửa trực tiếp danh sách và trả `None`. Hai hàm counted trả dict
và giữ cùng quyết định thuật toán như bản thường.

`minrun_length` giảm N bằng chia hai tới khi nhỏ hơn 64, ghi nhớ có bit
1 bị bỏ hay không. Ví dụ N=64 cho minrun=32, N=65 cho 33, N=127 cho 64.

`_count_run` xem cặp đầu để chọn chiều. Run tăng cho phép bằng nhau;
run giảm phải giảm nghiêm ngặt. Với `[5, 4a, 4b, 3]`, chỉ đảo `[5, 4a]`:
không đảo cả đoạn rồi làm `4b` đứng trước `4a`.

`_binary_insertion` tìm vị trí bằng tìm kiếm nhị phân rồi dời từng phần
tử sang phải. Với `[1, 4a, 4b, 3]`, khi chèn 3 sẽ dời 4b rồi 4a.
Nếu chèn một khóa 4 mới, nó nằm sau các khóa 4 cũ.

`node_power` lấy trung điểm hai run, chuẩn hóa theo N và tìm mức chia đôi
đầu tiên tách hai trung điểm. Dùng số nguyên để tránh sai số số thực.
Power càng lớn thì ranh giới càng sâu trong cây gộp.

`_push_run` tính power trước khi đẩy run mới vào stack. Khi power cũ lớn
hơn power mới, gộp run cũ trước. `_finish_merges` xử lý các run còn lại.
Ví dụ ba run dài 64, 64, 256 trong mảng 384 phần tử: gộp hai run 64 trước,
sau đó gộp run 128 với run 256.

`_merge` chép run ngắn hơn. Nếu chép trái, gộp từ đầu. Nếu chép phải,
gộp từ cuối. Phải đổi cách chọn khi bằng nhau để thứ tự cuối vẫn ổn định.

## Những câu cần tự trả lời

1. Tại sao dùng `right < left` rồi chọn trái ở nhánh còn lại?
   Vì bản ghi chỉ cần `__lt__`; nhánh còn lại gồm cả khóa bằng nhau,
   nên trái được giữ trước phải.
2. noA khác gì? Nó không dò run tự nhiên; mỗi khối minrun được sắp bằng
   Binary Insertion rồi đi qua cùng Powersort và merge.
3. Tại sao không đặt `counts += 1` ngay trong bản timing? Vì thao tác đếm
   làm thay đổi thời gian đang khảo sát. Bản counted dùng lượt riêng.
4. Độ phức tạp? Trường hợp xấu O(N log N), bộ nhớ phụ O(N). Đầu vào đã
   tăng hoặc giảm nghiêm ngặt được nhận diện bằng N−1 so sánh ở Timsort.
5. `run_count` có bằng R của D6 không? Không. R là số lô generator;
   ranh giới có thể nối thành run dài, và mở rộng minrun có thể hấp thụ
   các đoạn chưa được dò. Xem định nghĩa metric trong bàn giao Dân.
6. Timsort nhóm có giống `sorted()` hoàn toàn không? Bản nhóm viết Python
   và không có Galloping. `sorted()` là mốc thư viện, không dùng chênh
   lệch đó để kết luận riêng tác dụng nhận diện run.
7. Có thể kết luận noA luôn chậm hơn không? Chưa đo thì chưa kết luận.
   Mức giảm thời gian âm vẫn là kết quả hợp lệ.

Tự trace thêm `[2, 1]`, toàn khóa bằng nhau, N=65 và nhiều run độ dài
khác nhau. Tự giải thích từng nhánh trước khi trình bày với nhóm.
