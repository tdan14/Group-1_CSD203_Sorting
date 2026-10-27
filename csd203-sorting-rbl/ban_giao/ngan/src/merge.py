"""Stable top-down Merge Sort; author: Ngan, reviewer: My (pending).

One auxiliary list is allocated for N >= 2 and reused by every merge.
The timed path has no counters. Only ``<`` is required on element keys.
"""


def _merge(a: list, aux: list, lo: int, mid: int, hi: int) -> None:
    for index in range(lo, hi):
        aux[index] = a[index]

    left, right, dest = lo, mid, lo
    while left < mid and right < hi:
        left_value, right_value = aux[left], aux[right]
        # Taking the left value on ties preserves the original order.
        if right_value < left_value:
            a[dest] = right_value
            right += 1
        else:
            a[dest] = left_value
            left += 1
        dest += 1

    while left < mid:
        a[dest] = aux[left]
        left += 1
        dest += 1
    while right < hi:
        a[dest] = aux[right]
        right += 1
        dest += 1


def _sort(a: list, aux: list, lo: int, hi: int) -> None:
    if hi - lo < 2:
        return
    mid = (lo + hi) // 2
    _sort(a, aux, lo, mid)
    _sort(a, aux, mid, hi)
    _merge(a, aux, lo, mid, hi)


def sort(a: list) -> None:
    """Sort ``a`` in place, retaining the order of equivalent keys."""
    n = len(a)
    if n < 2:
        return
    aux = [None] * n
    _sort(a, aux, 0, n)


def _merge_counted(a: list, aux: list, lo: int, mid: int, hi: int,
                   counts: dict) -> None:
    for index in range(lo, hi):
        aux[index] = a[index]
        counts["array_reads"] += 1
        counts["array_writes"] += 1

    left, right, dest = lo, mid, lo
    while left < mid and right < hi:
        left_value, right_value = aux[left], aux[right]
        counts["array_reads"] += 2
        counts["key_comparisons"] += 1
        if right_value < left_value:
            a[dest] = right_value
            right += 1
        else:
            a[dest] = left_value
            left += 1
        counts["array_writes"] += 1
        dest += 1

    while left < mid:
        a[dest] = aux[left]
        counts["array_reads"] += 1
        counts["array_writes"] += 1
        left += 1
        dest += 1
    while right < hi:
        a[dest] = aux[right]
        counts["array_reads"] += 1
        counts["array_writes"] += 1
        right += 1
        dest += 1


def _sort_counted(a: list, aux: list, lo: int, hi: int, counts: dict) -> None:
    if hi - lo < 2:
        return
    mid = (lo + hi) // 2
    _sort_counted(a, aux, lo, mid, counts)
    _sort_counted(a, aux, mid, hi, counts)
    _merge_counted(a, aux, lo, mid, hi, counts)


def sort_counted(a: list) -> dict:
    """Sort with counts for key comparisons and reads/writes of a and aux.

    Initializing the N auxiliary slots counts as N writes. Index arithmetic,
    scalar variables, counters, and recursion bookkeeping are not counted.
    The algorithm and key-comparison order match ``sort``.
    """
    counts = {
        "key_comparisons": 0,
        "array_reads": 0,
        "array_writes": 0,
        "run_count": None,
        "avg_run_len": None,
    }
    n = len(a)
    if n < 2:
        return counts
    aux = [None] * n
    counts["array_writes"] = n
    _sort_counted(a, aux, 0, n, counts)
    return counts
