"""Quick Sort implementation with Hoare partition and Median-of-Three pivot.

Author: My (CSD203 RBL - Group 5)
Part of CSD203 Sorting Study.
"""

from typing import Any, Dict, List, Optional


def _read(a: List[Any], idx: int, cnt: Optional[Dict[str, Any]]) -> Any:
    """Read element at index idx from list a, tracking array reads if counting."""
    if cnt is not None:
        cnt["array_reads"] += 1
    return a[idx]


def _write(a: List[Any], idx: int, val: Any, cnt: Optional[Dict[str, Any]]) -> None:
    """Write val to list a at index idx, tracking array writes if counting."""
    if cnt is not None:
        cnt["array_writes"] += 1
    a[idx] = val


def _swap(a: List[Any], i: int, j: int, cnt: Optional[Dict[str, Any]]) -> None:
    """Swap elements at indices i and j in list a."""
    if i == j:
        return
    vi = _read(a, i, cnt)
    vj = _read(a, j, cnt)
    _write(a, i, vj, cnt)
    _write(a, j, vi, cnt)


def _median_of_three(
    a: List[Any], lo: int, hi: int, cnt: Optional[Dict[str, Any]]
) -> Any:
    """Sort a[lo], a[mid], a[hi] in-place and return the median at a[mid].

    Uses exactly 3 comparisons if hi - lo >= 2, or 1 comparison if hi - lo == 1.
    Pivot is fixed at a[mid].
    """
    mid = (lo + hi) // 2

    if hi - lo >= 2:
        # Comparison 1: a[lo] vs a[mid]
        v_lo = _read(a, lo, cnt)
        v_mid = _read(a, mid, cnt)
        if cnt is not None:
            cnt["key_comparisons"] += 1
        if v_lo > v_mid:
            _write(a, lo, v_mid, cnt)
            _write(a, mid, v_lo, cnt)

        # Comparison 2: a[mid] vs a[hi]
        v_mid = _read(a, mid, cnt)
        v_hi = _read(a, hi, cnt)
        if cnt is not None:
            cnt["key_comparisons"] += 1
        if v_mid > v_hi:
            _write(a, mid, v_hi, cnt)
            _write(a, hi, v_mid, cnt)

        # Comparison 3: a[lo] vs a[mid]
        v_lo = _read(a, lo, cnt)
        v_mid = _read(a, mid, cnt)
        if cnt is not None:
            cnt["key_comparisons"] += 1
        if v_lo > v_mid:
            _write(a, lo, v_mid, cnt)
            _write(a, mid, v_lo, cnt)

        return _read(a, mid, cnt)

    else:
        # hi - lo == 1: only 2 elements (mid == lo)
        v_lo = _read(a, lo, cnt)
        v_hi = _read(a, hi, cnt)
        if cnt is not None:
            cnt["key_comparisons"] += 1
        if v_lo > v_hi:
            _write(a, lo, v_hi, cnt)
            _write(a, hi, v_lo, cnt)
        return _read(a, mid, cnt)


def _hoare_partition(
    a: List[Any], lo: int, hi: int, cnt: Optional[Dict[str, Any]]
) -> int:
    """Hoare partition scheme with median-of-three pivot."""
    pivot = _median_of_three(a, lo, hi, cnt)

    i = lo - 1
    j = hi + 1

    while True:
        while True:
            i += 1
            val_i = _read(a, i, cnt)
            if cnt is not None:
                cnt["key_comparisons"] += 1
            if not (val_i < pivot):
                break

        while True:
            j -= 1
            val_j = _read(a, j, cnt)
            if cnt is not None:
                cnt["key_comparisons"] += 1
            if not (val_j > pivot):
                break

        if i >= j:
            return j

        _swap(a, i, j, cnt)


def _quick(a: List[Any], lo: int, hi: int, cnt: Optional[Dict[str, Any]]) -> None:
    """Recursive Quick Sort on subarray a[lo..hi]."""
    if lo < hi:
        p = _hoare_partition(a, lo, hi, cnt)
        _quick(a, lo, p, cnt)
        _quick(a, p + 1, hi, cnt)


def sort(a: List[Any]) -> None:
    """Sort list a in ascending order in-place using Quick Sort.

    No parameter validation, logging, CSV output, or operation counters are performed here.
    """
    if len(a) > 1:
        _quick(a, 0, len(a) - 1, None)


def sort_counted(a: List[Any]) -> Dict[str, Any]:
    """Sort list a in ascending order in-place and return operation metrics.

    Metrics include:
    - key_comparisons: number of key comparisons (including pivot selection)
    - array_reads: number of element reads from array a
    - array_writes: number of element writes to array a
    - run_count: None (not applicable to Quick Sort)
    - avg_run_len: None (not applicable to Quick Sort)
    """
    counts: Dict[str, Any] = {
        "key_comparisons": 0,
        "array_reads": 0,
        "array_writes": 0,
        "run_count": None,
        "avg_run_len": None,
    }
    if len(a) > 1:
        _quick(a, 0, len(a) - 1, counts)
    return counts
