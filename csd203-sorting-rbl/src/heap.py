"""Hải: Max-heap tại chỗ; build bottom-up; không heapq.

Đặt READY/COUNTED_READY=True sau khi triển khai và kiểm thử đúng; không dùng sorted/list.sort thay core.
"""
READY = False
COUNTED_READY = False

def sort(a):
    """Sắp xếp tăng dần trực tiếp a; trả None; timing không có bộ đếm."""
    raise NotImplementedError("Hải: triển khai heap.sort")

def sort_counted(a):
    """Cùng thuật toán; trả dict đủ trường trong src.contracts.METRIC_FIELDS."""
    raise NotImplementedError("Hải: triển khai heap.sort_counted")
