"""Dân: Timsort/Powersort không Galloping. noA chỉ tắt nhận diện run tự nhiên.

TODO: minrun 32..64; run không giảm/giảm ngặt; đảo run giảm; binary insertion;
Power theo bài gốc; ngăn xếp và merge dùng buffer run ngắn hơn; ổn định.
Các biến thể dùng chung cơ chế; không thay Powersort bằng merge tùy ý.
"""
READY = False
COUNTED_READY = False
NOA_READY = False
NOA_COUNTED_READY = False

def sort(a):
    raise NotImplementedError("Dân: triển khai Timsort/Powersort")

def sort_counted(a):
    raise NotImplementedError("Dân: triển khai bộ đếm Timsort")

def sort_noa(a):
    """Chia khối minrun cố định; binary insertion mỗi khối; giữ cùng Powersort/merge."""
    raise NotImplementedError("Dân: triển khai noA")

def sort_noa_counted(a):
    raise NotImplementedError("Dân: triển khai bộ đếm noA")
