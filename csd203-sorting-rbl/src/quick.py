"""My: Hoare partition; pivot median-of-three đầu/giữa/cuối; tại chỗ; không Lomuto/Insertion Sort.

Đặt READY/COUNTED_READY=True sau khi triển khai và kiểm thử đúng; không dùng sorted/list.sort thay core.
"""
READY = False
COUNTED_READY = False

def sort(a):
    """Sắp xếp tăng dần trực tiếp a; trả None; timing không có bộ đếm."""
    raise NotImplementedError("My: triển khai quick.sort")

def sort_counted(a):
    """Cùng thuật toán; trả dict đủ trường trong src.contracts.METRIC_FIELDS."""
    raise NotImplementedError("My: triển khai quick.sort_counted")
