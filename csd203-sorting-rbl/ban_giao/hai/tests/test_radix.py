"""Unit tests for Radix Sort (LSD 4-pass base 256).

Module: tests/test_radix.py
Author: Thien
Project: CSD203 Sorting RBL

Covers:
- Compulsory edge cases: [], [7], [2, 1], [3, 3, 3], [0, 2147483647, 0]
- 1,000 random cases of length 0-200 covering D1-D6 patterns with seed 203
- Cross-validation against Python's sorted()
- Equivalence validation between sort() and sort_counted()
"""

import random
import unittest
from src import radix

MAX_INT32 = (1 << 31) - 1  # 2147483647


class TestRadixSort(unittest.TestCase):
    def test_compulsory_edge_cases(self) -> None:
        """Verify the mandatory edge cases specified in the project requirements."""
        test_cases = [
            [],
            [7],
            [2, 1],
            [3, 3, 3],
            [0, MAX_INT32, 0],
            [MAX_INT32, 0, MAX_INT32, 100, 1],
        ]

        for orig in test_cases:
            with self.subTest(orig=orig):
                expected = sorted(orig)

                # Test standard sort
                a = list(orig)
                radix.sort(a)
                self.assertEqual(a, expected, f"Failed standard sort for input {orig}")

                # Test sort_counted
                a_counted = list(orig)
                stats = radix.sort_counted(a_counted)
                self.assertEqual(a_counted, expected, f"Failed sort_counted for input {orig}")
                self.assertIsNone(stats["key_comparisons"])
                self.assertIsNone(stats["run_count"])
                self.assertIsNone(stats["avg_run_len"])
                self.assertIsInstance(stats["array_reads"], int)
                self.assertIsInstance(stats["array_writes"], int)

    def test_1000_fuzz_cases_d1_to_d6(self) -> None:
        """Run 1,000 fuzz test cases covering D1-D6 variations with length 0-200.

        Using dedicated seed 203 to avoid collision with benchmark seeds (2026, 2027, 2028).
        """
        rng = random.Random(203)

        for case_idx in range(1000):
            n = rng.randint(0, 200)
            pattern_type = case_idx % 6

            if n == 0:
                data = []
            elif pattern_type == 0:
                # D1: Random integers in [0, 2^31 - 1]
                data = [rng.randint(0, MAX_INT32) for _ in range(n)]
            elif pattern_type == 1:
                # D2: Already sorted
                data = sorted([rng.randint(0, MAX_INT32) for _ in range(n)])
            elif pattern_type == 2:
                # D3: Nearly sorted (swap a few pairs)
                data = sorted([rng.randint(0, MAX_INT32) for _ in range(n)])
                num_swaps = max(1, n // 10) if n > 2 else 0
                for _ in range(num_swaps):
                    i, j = rng.randint(0, n - 1), rng.randint(0, n - 1)
                    data[i], data[j] = data[j], data[i]
            elif pattern_type == 3:
                # D4: Reverse sorted
                data = sorted([rng.randint(0, MAX_INT32) for _ in range(n)], reverse=True)
            elif pattern_type == 4:
                # D5: Many duplicate keys (K distinct values)
                k = rng.choice([2, 5, 10, 20])
                pool = [rng.randint(0, MAX_INT32) for _ in range(k)]
                data = [rng.choice(pool) for _ in range(n)]
            else:
                # D6: Concatenated sorted chunks
                r = rng.choice([2, 4, 8])
                chunk_size = max(1, n // r)
                chunks = []
                for start_idx in range(0, n, chunk_size):
                    chunk = [rng.randint(0, MAX_INT32) for _ in range(min(chunk_size, n - start_idx))]
                    chunk.sort()
                    chunks.extend(chunk)
                data = chunks[:n]

            expected = sorted(data)

            # Test sort(a)
            a = list(data)
            radix.sort(a)
            self.assertEqual(a, expected, f"Case {case_idx} failed sort()")

            # Test sort_counted(a)
            a_counted = list(data)
            stats = radix.sort_counted(a_counted)
            self.assertEqual(a_counted, expected, f"Case {case_idx} failed sort_counted()")

            # Check stats consistency
            if n > 1:
                self.assertGreater(stats["array_reads"], 0)
                self.assertGreater(stats["array_writes"], 0)
            else:
                self.assertEqual(stats["array_reads"], 0)
                self.assertEqual(stats["array_writes"], 0)


if __name__ == "__main__":
    unittest.main()
