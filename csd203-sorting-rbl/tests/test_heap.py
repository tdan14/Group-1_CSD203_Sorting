"""Unit tests for Heap Sort.

Module: tests/test_heap.py
Author: Hai (rq2-hai)
Reviewer: Thien (rq2-thien)
Project: CSD203 Sorting RBL

Covers (group plan, "Bo test bat buoc"):
- Compulsory edge cases: [], [7], [2, 1], [3, 3, 3], [0, 2147483647, 0]
- 1,000 fuzz cases, length 0-200, covering D1-D6 patterns, seed 203
  (generated with data.generate so the patterns match the benchmark exactly;
   D6 with R > N gives empty batches, which the plan allows)
- sort() and sort_counted() must give the same output
- Implementation checks: no heapq, counters consistent with the algorithm
"""

import random
import unittest

from data.generate import generate
from src import heap

MAX_INT32 = (1 << 31) - 1
FUZZ_SEED = 203

EDGE_CASES = [
    [],
    [7],
    [2, 1],
    [3, 3, 3],
    [0, MAX_INT32, 0],
    [5, 1, 4, 2, 8, 0, 2],
    [MAX_INT32, MAX_INT32 - 1, 0, 1],
]


def fuzz_cases(count: int = 1000):
    """Yields (label, data) covering D1-D6 with all K and R levels."""
    rng = random.Random(FUZZ_SEED)
    families = [
        ("D1", None, None), ("D2", None, None), ("D3", None, None), ("D4", None, None),
        ("D5", 1000, None), ("D5", 10, None), ("D5", 2, None),
        ("D6", None, 2), ("D6", None, 16), ("D6", None, 256),
    ]
    for i in range(count):
        ds, k, r = families[i % len(families)]
        n = rng.randint(0, 200)
        seed = rng.randint(0, 10**9)
        data = generate(ds, n, seed, k=k, runs=r)
        if ds == "D3" and n >= 2:
            # D3 at N <= 200 has 0 swaps by spec; add a few swaps so the
            # "nearly sorted" pattern is actually exercised in the test.
            for _ in range(max(1, n // 20)):
                a, b = rng.sample(range(n), 2)
                data[a], data[b] = data[b], data[a]
        yield f"{ds}(K={k},R={r},n={n})", data


class TestHeapSort(unittest.TestCase):
    def test_compulsory_edge_cases(self) -> None:
        for orig in EDGE_CASES:
            with self.subTest(orig=orig):
                expected = sorted(orig)

                a = list(orig)
                self.assertIsNone(heap.sort(a))
                self.assertEqual(a, expected)

                a_cnt = list(orig)
                stats = heap.sort_counted(a_cnt)
                self.assertEqual(a_cnt, expected)
                self.assertIsInstance(stats["key_comparisons"], int)
                self.assertIsInstance(stats["array_reads"], int)
                self.assertIsInstance(stats["array_writes"], int)
                self.assertIsNone(stats["run_count"])
                self.assertIsNone(stats["avg_run_len"])

    def test_1000_fuzz_cases_d1_to_d6(self) -> None:
        for label, data in fuzz_cases(1000):
            expected = sorted(data)

            a = list(data)
            heap.sort(a)
            self.assertEqual(a, expected, f"sort() failed on {label}")

            a_cnt = list(data)
            heap.sort_counted(a_cnt)
            self.assertEqual(a_cnt, expected, f"sort_counted() failed on {label}")

    def test_sort_and_sort_counted_same_output_large(self) -> None:
        for ds, k, r in [("D1", None, None), ("D2", None, None), ("D4", None, None),
                         ("D5", 2, None), ("D6", None, 16)]:
            data = generate(ds, 5000, 2026, k=k, runs=r)
            a, b = list(data), list(data)
            heap.sort(a)
            heap.sort_counted(b)
            self.assertEqual(a, b, ds)
            self.assertEqual(a, sorted(data), ds)

    def test_counter_values_are_plausible(self) -> None:
        # Heap Sort uses Theta(n log n) comparisons; at most ~2 n log2 n.
        n = 4096
        data = generate("D1", n, 2026)
        stats = heap.sort_counted(list(data))
        self.assertGreater(stats["key_comparisons"], n)
        self.assertLess(stats["key_comparisons"], 2 * n * 12 + n)
        # Every sift ends with one write, so writes >= number of sifts (n//2 + n-1).
        self.assertGreaterEqual(stats["array_writes"], n // 2 + n - 1)

    def test_counted_small_exact(self) -> None:
        # [2, 1]: build sifts root 0 (1 comparison, child has no sibling),
        # then one sort-down step with an empty heap (no comparison).
        stats = heap.sort_counted([2, 1])
        self.assertEqual(stats["key_comparisons"], 1)

    def test_does_not_use_heapq(self) -> None:
        import inspect
        source = inspect.getsource(heap)
        self.assertNotIn("import heapq", source)
        self.assertNotIn("from heapq", source)


if __name__ == "__main__":
    unittest.main()
