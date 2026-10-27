# Kết quả

Chưa có kết quả nghiên cứu trong bộ khung.

- raw/<run_id>/: measurements.csv + manifest.json do benchmark chính thức sinh.
- smoke/<run_id>/: test hạ tầng, đã gitignore, không dùng kết luận paper.
- summary/: kết quả median/min/max từ script summarize.
- figures/: hình tạo từ summary/CSV thật.

Không sửa/ghi đè CSV gốc; mỗi lần chạy có run_id mới. Commit raw CSV/manifest cần nộp cùng source và ghi checksum/version. Không đưa dữ liệu lớn tái tạo được vào Git. Hình timeout chưa hoàn thành không được vẽ như thời gian hoàn thành chính xác.
