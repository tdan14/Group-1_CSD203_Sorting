"""Thiện: LSD cơ số 256; đúng 4 lượt; Counting Sort stable; miền [0, 2**31-1].

Đặt READY/COUNTED_READY=True sau khi triển khai và kiểm thử đúng; không dùng sorted/list.sort thay core.
"""
READY = False
COUNTED_READY = False

def sort(a):
    """Sắp xếp tăng dần trực tiếp a; trả None; timing không có bộ đếm."""
    raise NotImplementedError("Thiện: triển khai radix.sort")

def sort_counted(a):
    """Cùng thuật toán; trả dict đủ trường trong src.contracts.METRIC_FIELDS."""
    raise NotImplementedError("Thiện: triển khai radix.sort_counted")
