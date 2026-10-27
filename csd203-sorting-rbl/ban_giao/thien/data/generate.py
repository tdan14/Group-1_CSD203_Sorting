"""Data Generator for CSD203 Sorting RBL.

Module: data/generate.py
Specification:
- Seed values: 2026, 2027, 2028 (or user specified)
- Domain: integers in [0, 2^31 - 1] (unsigned 32-bit range [0, 2147483647])
- Datasets:
    D1: Random integers using random.Random(seed)
    D2: Sorted D1 (ascending)
    D3: D2 with floor(N / 1000) random pair swaps using random.Random(seed + 10000)
    D4: Reverse sorted D2 (descending)
    D5: Pick K distinct values uniformly, then sample N elements from them
    D6: Divide D1 into R contiguous chunks (remainder distributed to first chunks),
        sort each chunk independently, then concatenate
- input_sha256: SHA-256 of the sequence encoded as 32-bit unsigned little-endian integers
- output_check: Checksum h = (31 * h + x) mod 2^64 with h = 0 initially
"""

import hashlib
import math
import random
import struct
from typing import Optional

MAX_INT32 = (1 << 31) - 1
GENERATOR_VERSION = "1.0.0"


def compute_input_sha256(data: list[int]) -> str:
    """Computes SHA-256 of array data packed as unsigned 32-bit little-endian."""
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
    """Generates synthetic dataset according to project specifications.

    Args:
        dataset: One of 'D1', 'D2', 'D3', 'D4', 'D5', 'D6'
        n: Size of dataset
        seed: Random seed
        k: Number of distinct keys for D5 (required for D5)
        runs: Number of chunks R for D6 (required for D6)

    Returns:
        list[int]
    """
    dataset = dataset.upper()

    # D1 generation
    rng = random.Random(seed)
    d1 = [rng.randint(0, MAX_INT32) for _ in range(n)]

    if dataset == "D1":
        return d1

    # D2 generation
    d2 = sorted(d1)
    if dataset == "D2":
        return d2

    # D3 generation
    if dataset == "D3":
        d3 = list(d2)
        if n >= 1000:
            swap_rng = random.Random(seed + 10000)
            swaps = math.floor(n / 1000)
            for _ in range(swaps):
                i = swap_rng.randint(0, n - 1)
                j = swap_rng.randint(0, n - 1)
                d3[i], d3[j] = d3[j], d3[i]
        return d3

    # D4 generation
    if dataset == "D4":
        return list(reversed(d2))

    # D5 generation
    if dataset == "D5":
        if k is None or k <= 0:
            raise ValueError("Parameter k must be a positive integer for dataset D5")
        actual_k = min(k, n)
        # Sample k distinct values without replacement
        distinct_vals = rng.sample(range(MAX_INT32 + 1), actual_k)
        return [rng.choice(distinct_vals) for _ in range(n)]

    # D6 generation
    if dataset == "D6":
        if runs is None or runs <= 0:
            raise ValueError("Parameter runs (R) must be a positive integer for dataset D6")
        r = runs
        base_size = n // r
        rem = n % r

        result = []
        curr = 0
        for i in range(r):
            chunk_len = base_size + (1 if i < rem else 0)
            chunk = d1[curr : curr + chunk_len]
            chunk.sort()
            result.extend(chunk)
            curr += chunk_len
        return result

    raise ValueError(f"Unknown dataset type: {dataset}")
