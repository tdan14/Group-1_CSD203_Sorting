"""Radix Sort (LSD) Implementation.

Module: src/radix.py
Author: Thien (rq2-thien)
Project: CSD203 Sorting RBL - AI Pipeline Data

Specification:
- LSD (Least Significant Digit) Radix Sort, base 256 (2^8).
- Exactly 4 passes for 32-bit unsigned integers in range [0, 2^31 - 1].
- Each pass executes a stable Counting Sort on the respective byte:
    Pass 0: bits 0-7   ((x >> 0) & 0xFF)
    Pass 1: bits 8-15  ((x >> 8) & 0xFF)
    Pass 2: bits 16-23 ((x >> 16) & 0xFF)
    Pass 3: bits 24-31 ((x >> 24) & 0xFF)
- In-place modification of list `a`.
- Standard interface:
    sort(a) -> None
- Counted interface:
    sort_counted(a) -> dict
"""

from typing import Any, Optional


def sort(a: list[int]) -> None:
    """Sorts list `a` in ascending order in-place using 4-pass LSD Radix Sort (base 256).

    Pure Python implementation without input checks, logging, or measurement overhead.
    """
    n = len(a)
    if n <= 1:
        return

    # Output buffer reused across passes or allocated per pass
    output = [0] * n

    # Exactly 4 passes for 32-bit integers (byte 0 to byte 3)
    for shift in (0, 8, 16, 24):
        count = [0] * 256

        # 1. Count occurrences of each byte value
        for x in a:
            count[(x >> shift) & 0xFF] += 1

        # 2. Cumulative prefix sum to find target positions
        for j in range(1, 256):
            count[j] += count[j - 1]

        # 3. Stable placement from right to left (preserves relative order)
        for idx in range(n - 1, -1, -1):
            val = a[idx]
            byte_val = (val >> shift) & 0xFF
            pos = count[byte_val] - 1
            count[byte_val] = pos
            output[pos] = val

        # 4. Copy back to list `a`
        a[:] = output


def sort_counted(a: list[int]) -> dict[str, Optional[int]]:
    """Sorts list `a` in ascending order in-place and counts array operations.

    Tracks:
    - array_reads: reads from input list `a`, temp array `output`, and counting array `count`
    - array_writes: writes to input list `a`, temp array `output`, and counting array `count`

    Returns:
        dict with keys:
            key_comparisons: None (Radix is non-comparative)
            array_reads: int
            array_writes: int
            run_count: None (Not applicable)
            avg_run_len: None (Not applicable)
    """
    n = len(a)
    if n <= 1:
        return {
            "key_comparisons": None,
            "array_reads": 0,
            "array_writes": 0,
            "run_count": None,
            "avg_run_len": None,
        }

    reads = 0
    writes = 0

    output = [0] * n
    writes += n  # Allocation / initialization of output array

    for shift in (0, 8, 16, 24):
        count = [0] * 256
        writes += 256  # Initialization of 256 buckets

        # 1. Count occurrences of each byte
        for idx in range(n):
            val = a[idx]
            reads += 1  # Read a[idx]
            byte_val = (val >> shift) & 0xFF
            prev_cnt = count[byte_val]
            reads += 1  # Read count[byte_val]
            count[byte_val] = prev_cnt + 1
            writes += 1  # Write count[byte_val]

        # 2. Cumulative prefix sums
        for j in range(1, 256):
            c_prev = count[j - 1]
            c_curr = count[j]
            reads += 2  # Read count[j-1] and count[j]
            count[j] = c_prev + c_curr
            writes += 1  # Write count[j]

        # 3. Stable placement from right to left
        for idx in range(n - 1, -1, -1):
            val = a[idx]
            reads += 1  # Read a[idx]
            byte_val = (val >> shift) & 0xFF

            pos = count[byte_val] - 1
            reads += 1  # Read count[byte_val]
            count[byte_val] = pos
            writes += 1  # Write count[byte_val]

            output[pos] = val
            writes += 1  # Write output[pos]

        # 4. Copy back to array `a`
        for idx in range(n):
            val = output[idx]
            reads += 1  # Read output[idx]
            a[idx] = val
            writes += 1  # Write a[idx]

    return {
        "key_comparisons": None,
        "array_reads": reads,
        "array_writes": writes,
        "run_count": None,
        "avg_run_len": None,
    }
