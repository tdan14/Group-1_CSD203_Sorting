"""Unit tests and review test suite for Heap Sort.

Module: tests/test_heap.py
Reviewer: Thien (rq2-thien)
Author: Hai (rq2-hai)
Project: CSD203 Sorting RBL
"""

import random
import unittest
from src import heap

MAX_INT32 = (1 << 31) - 1


class TestHeapSort(unittest.TestCase):
    def test_compulsory_edge_cases(self) -> None:
        """Verify the mandatory edge cases specified in the project requirements."""
        test_cases = [
            [],
            [7],
            [2, 1],
            [3, 3, 3],
            [0, MAX_INT32, 0],
            [5, 1, 4, 2, 8, 0, 2],
        ]

        for orig in test_cases:
            with self.subTest(orig=orig):
                expected = sorted(orig)

                # Standard sort
                a = list(orig)
                heap.sort(a)
                self.assertEqual(a, expected, f"Heap sort failed for {orig}")

                # Counted sort
                a_cnt = list(orig)
                stats = heap.sort_counted(a_cnt)
                self.assertEqual(a_cnt, expected, f"Heap sort_counted failed for {orig}")
                self.assertIsInstance(stats["key_comparisons"], int)
                self.assertIsInstance(stats["array_reads"], int)
                self.assertIsInstance(stats["array_writes"], int)
                self.assertIsNone(stats["run_count"])
                self.assertIsNone(stats["avg_run_len"])

    def test_1000_fuzz_cases(self) -> None:
        """Run 1,000 fuzz cases of length 0-200 with seed 203."""
        rng = random.Random(203)
        for _ in range(1000):
            n = rng.randint(0, 200)
            data = [rng.randint(0, MAX_INT32) for _ in range(n)]
            expected = sorted(data)

            a = list(data)
            heap.sort(a)
            self.assertEqual(a, expected)

            a_cnt = list(data)
            stats = heap.sort_counted(a_cnt)
            self.assertEqual(a_cnt, expected)


if __name__ == "__main__":
    unittest.main()
