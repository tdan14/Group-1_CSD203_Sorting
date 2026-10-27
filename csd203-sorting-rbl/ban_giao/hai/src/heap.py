"""Heap Sort (max-heap, tại chỗ, dựng heap bottom-up).

Module: src/heap.py
Author: Hai (rq2-hai)
Reviewer: Thien (rq2-thien)
Project: CSD203 Sorting RBL

Đặc tả (đề tài, mục 3):
- Max-heap tại chỗ trên chính danh sách `a`.
- Pha dựng heap theo bottom-up: sift-down từ nút trong cuối cùng
  (chỉ số n//2 - 1) lùi về 0.
- Không dùng thư viện heapq.
- Chỉ dùng phép so sánh `<` trên khóa.

Thuật toán (Williams, 1964):
  1. Dựng heap: với i = n//2 - 1, ..., 0 -> sift_down tại i trong a[0:n].
     Sau bước này a[0] là phần tử lớn nhất.
  2. Rút gọn: với end = n-1, ..., 1:
       - giữ x = a[end], đưa max a[0] về vị trí end (vị trí cuối cùng của nó),
       - cho x chìm xuống từ gốc trong heap con a[0:end].

Sift-down dùng kỹ thuật "lỗ hổng" (hole): giữ phần tử đang chìm trong biến
`item`, chỉ chép con lớn hơn lên trên, ghi `item` một lần ở cuối. Cách này
ít lần ghi mảng hơn hoán đổi từng tầng, còn số phép so sánh và thứ tự quyết
định thì không đổi.

Heap Sort không ổn định (đề không yêu cầu ổn định cho Heap).

Giao diện:
    sort(a) -> None              : sắp xếp tăng dần tại chỗ, không đếm
    sort_counted(a) -> dict      : cùng quyết định thuật toán, có đếm
"""

from typing import Optional


def _sift_down(a: list, item, root: int, end: int) -> None:
    """Đặt `item` vào vị trí `root` rồi cho nó chìm xuống trong heap a[0:end].

    Bất biến: hai cây con của `root` đã là max-heap.
    """
    child = 2 * root + 1
    while child < end:
        child_val = a[child]
        right = child + 1
        if right < end:
            right_val = a[right]
            # Chọn con lớn hơn; nếu bằng nhau giữ con trái.
            if child_val < right_val:
                child = right
                child_val = right_val
        # child_val là giá trị của con lớn hơn.
        if item < child_val:
            a[root] = child_val     # đẩy con lớn hơn lên lỗ hổng
            root = child
            child = 2 * root + 1
        else:
            break
    a[root] = item


def sort(a: list) -> None:
    """Sắp xếp tăng dần tại chỗ bằng Heap Sort (max-heap, bottom-up).

    Không kiểm tra đầu vào, không ghi log, không đếm.
    """
    n = len(a)
    if n <= 1:
        return

    # 1. Dựng max-heap bottom-up: từ nút trong cuối cùng lùi về gốc.
    for start in range(n // 2 - 1, -1, -1):
        _sift_down(a, a[start], start, n)

    # 2. Lần lượt đưa max về cuối và thu nhỏ heap.
    for end in range(n - 1, 0, -1):
        item = a[end]
        a[end] = a[0]
        _sift_down(a, item, 0, end)


def sort_counted(a: list) -> dict[str, Optional[int]]:
    """Cùng thuật toán như sort(a), có đếm phép toán.

    Quy ước đếm (khớp với từng dòng của sort/_sift_down):
    - key_comparisons: mỗi phép `<` giữa hai khóa.
    - array_reads: mỗi lần đọc a[i].
    - array_writes: mỗi lần ghi a[i] = ...
    - run_count, avg_run_len: None (không áp dụng cho Heap Sort).

    Phần đếm được viết riêng, không chèn vào sort(a), theo quy định
    "tắt bộ đếm khi đo thời gian".
    """
    comparisons = 0
    reads = 0
    writes = 0

    n = len(a)
    if n <= 1:
        return {
            "key_comparisons": 0,
            "array_reads": 0,
            "array_writes": 0,
            "run_count": None,
            "avg_run_len": None,
        }

    def sift_down_counted(item, root: int, end: int) -> None:
        nonlocal comparisons, reads, writes
        child = 2 * root + 1
        while child < end:
            child_val = a[child]
            reads += 1
            right = child + 1
            if right < end:
                right_val = a[right]
                reads += 1
                comparisons += 1
                if child_val < right_val:
                    child = right
                    child_val = right_val
            comparisons += 1
            if item < child_val:
                a[root] = child_val
                writes += 1
                root = child
                child = 2 * root + 1
            else:
                break
        a[root] = item
        writes += 1

    # 1. Dựng heap
    for start in range(n // 2 - 1, -1, -1):
        item = a[start]
        reads += 1
        sift_down_counted(item, start, n)

    # 2. Rút gọn
    for end in range(n - 1, 0, -1):
        item = a[end]
        reads += 1
        top = a[0]
        reads += 1
        a[end] = top
        writes += 1
        sift_down_counted(item, 0, end)

    return {
        "key_comparisons": comparisons,
        "array_reads": reads,
        "array_writes": writes,
        "run_count": None,
        "avg_run_len": None,
    }
