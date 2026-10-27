"""Dataset generation module for sorting benchmarks.

CSD203 RBL Sorting Research Project.
Authors: My (D1-D3), Ngan (D4-D6).
"""

import math
import random
from typing import List, Optional


def generate(
    dataset: str,
    n: int,
    seed: int,
    k: Optional[int] = None,
    runs: Optional[int] = None,
) -> List[int]:
    """Generate benchmark dataset according to project specifications.

    Parameters:
    - dataset: 'D1'..'D6'
    - n: number of elements
    - seed: random seed (official: 2026, 2027, 2028; fuzz: 203)
    - k: distinct keys for D5 (not applicable to D1-D3)
    - runs: number of batches for D6 (not applicable to D1-D3)

    Returns:
    - list of integers in range [0, 2^31 - 1]
    """
    if n <= 0:
        return []

    if dataset == "D1":
        # D1: Uniform random integers in [0, 2^31 - 1]
        rng = random.Random(seed)
        return [rng.randrange(2**31) for _ in range(n)]

    if dataset == "D2":
        # D2: Sorted D1 (strictly ascending / non-decreasing)
        return sorted(generate("D1", n, seed))

    if dataset == "D3":
        # D3: Almost sorted. Start from D2, perform floor(n / 1000) swaps
        # of two distinct positions. Position rng stream: seed + 10000.
        base = generate("D2", n, seed)
        swap_count = math.floor(n / 1000)
        if swap_count > 0 and n >= 2:
            swap_rng = random.Random(seed + 10000)
            for _ in range(swap_count):
                i = swap_rng.randrange(n)
                j = swap_rng.randrange(n)
                while j == i:
                    j = swap_rng.randrange(n)
                base[i], base[j] = base[j], base[i]
        return base

    if dataset in ("D4", "D5", "D6"):
        raise NotImplementedError(
            f"Dataset {dataset} do Ngan phu trach trien khai trong cung file"
        )

    raise ValueError(f"Unknown dataset: {dataset}")
