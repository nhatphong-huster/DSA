PHẦN 1: TỔNG QUAN VÀ PHÂN TÍCH (5-7 trang)
Giới thiệu bài toán: Định nghĩa trò chơi Sudoku 9x9.
Phân tích đầu vào/đầu ra: Input là file .txt chứa ma trận, Output là ma trận đã giải.
Lựa chọn cấu trúc dữ liệu: Tại sao dùng mảng 2 chiều (2D Array)? (Giải thích về độ phức tạp bộ nhớ O(N^2)).
PHẦN 2: THIẾT KẾ HỆ THỐNG (5-7 trang)
Sơ đồ lớp (Class Diagram):
Class SudokuSolver: Chứa các phương thức giải.
Class FileManager: Xử lý đọc/ghi file.
Class Main: Điều khiển luồng chương trình.


Mô tả các module: Chức năng cụ thể của từng hàm.
PHẦN 3: TRIỂN KHAI THUẬT TOÁN (10-15 trang)
Thuật toán chính (Backtracking):
Giả mã (Pseudocode) cho hàm solveSudoku().
Giải thích logic: Tìm ô trống -> Thử số (1-9) -> Kiểm tra an toàn -> Gọi đệ quy -> Quay lui nếu sai.


Phân tích độ phức tạp:
Độ phức tạp thời gian: O(9^(n*n)) trong trường hợp xấu nhất.
Giải thích lý do chọn Backtracking (phù hợp với không gian tìm kiếm của Sudoku).
Lập trình: Các đoạn mã nguồn quan trọng (Core logic).
PHẦN 4: KẾT QUẢ VÀ KIỂM THỬ (5-8 trang)
Bộ dữ liệu test: Giới thiệu các bảng Sudoku từ dễ đến cực khó.
Đo lường hiệu năng (Performance Test):
Bảng kết quả: Thời gian giải (ms) cho các mức độ khác nhau.
Đồ thị so sánh thời gian thực thi.
Kết quả thực tế: Hình ảnh/Video minh họa chương trình chạy thành công.
PHẦN 5: KẾT LUẬN VÀ ĐÁNH GIÁ (2-3 trang)
Ưu điểm và hạn chế của phương pháp hiện tại.
Hướng phát triển (ví dụ: tối ưu bằng thuật toán Dancing Links hoặc dùng GUI để tăng trải nghiệm).
Đánh giá cá nhân: Mỗi thành viên tự ghi nhận mức độ hoàn thành công việc.

Mọi người sử dụng fixed.py để làm các phần sau nhé. Mình đã sửa lại file code cho cả bài 


