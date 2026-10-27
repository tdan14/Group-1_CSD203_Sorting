# Dữ liệu

`generate(dataset,n,seed,k=None,runs=None)` trong generate.py là generator tham chiếu có sẵn để khởi động hạ tầng. My/Ngân review và chịu trách nhiệm phiên bản sử dụng chính thức.

D1 ngẫu nhiên đều; D2 sorted D1; D3 swap N//1000 cặp trên D2 với RNG seed+10000; D4 đảo D2; D5 K khóa phân biệt; D6 R đoạn liên tiếp đã sorted. Trong fuzz, N<R cho phép lô rỗng; R là số lô, không khẳng định đúng bằng số run tự nhiên.

D1–D4 không truyền k/runs. D5 bắt buộc k; D6 bắt buộc runs. Không truyền tham số thừa. Miền số là 0..2147483647. sorted trong generator dùng chuẩn bị dữ liệu, hoàn toàn ngoài vùng đo thuật toán.

Lưu dữ liệu mẫu nhỏ vào samples/ nếu cần; dữ liệu lớn tái tạo từ config/seed/generator_version/input_sha256 trong manifest/CSV.
