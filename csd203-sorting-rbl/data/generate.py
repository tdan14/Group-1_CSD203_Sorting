"""Data Generator for CSD203 Sorting RBL.

Module: data/generate.py
Specification:
- Seed values: 2026, 2027, 2028 (or user specified)
- Domain: integers in [0, 2^31 - 1]
- Datasets:
    D1: Random integers using random.Random(seed)
    D2: Sorted D1 (ascending)
    D3: D2 with floor(N / 1000) swaps of two DISTINCT positions,
        positions drawn from random.Random(seed + 10000).
        Positions may repeat across different swaps. N < 1000 -> 0 swaps.
    D4: Reverse of D2 (descending)
    D5: Sample K distinct values without replacement from the domain,
        then draw N elements uniformly from that set.
    D6: Divide D1 into R contiguous chunks (remainder distributed to the
        first chunks, lengths differ by at most 1), sort each chunk,
        then concatenate. R is the number of generated batches, not the
        number of natural runs Timsort will detect.
- input_sha256: SHA-256 of the sequence encoded as uint32 little-endian
- output_check: h = (31 * h + x) mod 2^64, h = 0 initially

Changelog:
- 1.1.0: D3 now swaps two distinct positions (rng.sample) as required by the
         group plan. v1.0.0 could pick i == j, producing a no-op swap.
         rng.sample(range(n), 2) draws the same random stream as two
         randint(0, n-1) calls and only redraws when i == j, so the output
         differs from v1.0.0 only for seeds where that collision happens.
         Verified: for the official seeds 2026/2027/2028 at N = 100k and 1M,
         D3 is bit-identical to v1.0.0 (no collision). Example of a fixed
         case: seed 2798, N = 1000.
         D1, D2, D4, D5, D6 outputs are unchanged from v1.0.0.
"""

import hashlib
import random
import struct
from typing import Optional

MAX_INT32 = (1 << 31) - 1
GENERATOR_VERSION = "1.1.0"

DATASETS = ("D1", "D2", "D3", "D4", "D5", "D6")


def compute_input_sha256(data: list[int]) -> str:
    """Computes SHA-256 of the data packed as unsigned 32-bit little-endian."""
    hasher = hashlib.sha256()
    chunk_size = 10000
    for i in range(0, len(data), chunk_size):
        chunk = data[i : i + chunk_size]
        hasher.update(struct.pack(f"<{len(chunk)}I", *chunk))
    return hasher.hexdigest()


def compute_output_check(data: list[int]) -> int:
    """Computes output_check checksum: h = (31 * h + x) mod 2^64."""
    h = 0
    mod = 1 << 64
    for x in data:
        h = (31 * h + x) % mod
    return h


def generate(
    dataset: str,
    n: int,
    seed: int,
    k: Optional[int] = None,
    runs: Optional[int] = None,
) -> list[int]:
    """Generates a synthetic dataset according to the project specification.

    Args:
        dataset: One of 'D1'..'D6'
        n: Number of elements (>= 0)
        seed: Random seed
        k: Number of distinct keys for D5 (required for D5)
        runs: Number of batches R for D6 (required for D6)
    """
    dataset = dataset.upper()
    if dataset not in DATASETS:
        raise ValueError(f"Unknown dataset type: {dataset}")
    if n < 0:
        raise ValueError("n must be >= 0")
    if dataset == "D5" and (k is None or k <= 0):
        raise ValueError("Parameter k must be a positive integer for dataset D5")
    if dataset == "D6" and (runs is None or runs <= 0):
        raise ValueError("Parameter runs (R) must be a positive integer for dataset D6")

    # D1 is the base of every dataset. The same rng continues to be used by D5,
    # so the call order below must not change (it keeps D5 reproducible).
    rng = random.Random(seed)
    d1 = [rng.randint(0, MAX_INT32) for _ in range(n)]

    if dataset == "D1":
        return d1

    if dataset in ("D2", "D3", "D4"):
        d2 = sorted(d1)
        if dataset == "D2":
            return d2
        if dataset == "D4":
            d2.reverse()
            return d2
        # D3: floor(N/1000) swaps of two distinct positions.
        swaps = n // 1000
        if swaps > 0:
            swap_rng = random.Random(seed + 10000)
            positions = range(n)
            for _ in range(swaps):
                i, j = swap_rng.sample(positions, 2)
                d2[i], d2[j] = d2[j], d2[i]
        return d2

    if dataset == "D5":
        # Cannot draw more distinct values than elements requested
        # (only matters for tiny N, e.g. warm-up or tests).
        actual_k = min(k, n)
        distinct_vals = rng.sample(range(MAX_INT32 + 1), actual_k)
        return [rng.choice(distinct_vals) for _ in range(n)]

    # D6
    r = runs
    base_size, rem = divmod(n, r)
    result: list[int] = []
    curr = 0
    for i in range(r):
        chunk_len = base_size + (1 if i < rem else 0)
        chunk = d1[curr : curr + chunk_len]
        chunk.sort()
        result.extend(chunk)
        curr += chunk_len
    return result
