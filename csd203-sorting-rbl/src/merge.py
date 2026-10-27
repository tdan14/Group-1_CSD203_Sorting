"""Ngân: Top-down; một mảng phụ N tái sử dụng; stable; hỗ trợ đối tượng chỉ có __lt__.

Đặt READY/COUNTED_READY=True sau khi triển khai và kiểm thử đúng; không dùng sorted/list.sort thay core.
"""
READY = False
COUNTED_READY = False

def sort(a):
    """Sắp xếp tăng dần trực tiếp a; trả None; timing không có bộ đếm."""
    raise NotImplementedError("Ngân: triển khai merge.sort")

def sort_counted(a):
    """Cùng thuật toán; trả dict đủ trường trong src.contracts.METRIC_FIELDS."""
    raise NotImplementedError("Ngân: triển khai merge.sort_counted")
