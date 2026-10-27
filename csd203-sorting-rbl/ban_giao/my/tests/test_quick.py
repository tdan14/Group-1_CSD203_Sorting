"""Unit and fuzz tests for Quick Sort module (src/quick.py).

CSD203 RBL Sorting Research Project.
Author: My
Reviewer: Ngan
"""

import math
import random
import unittest
from typing import List

from data.generate import generate
import src.quick as quick


def _generate_mock_d4_to_d6(dataset: str, n: int, seed: int) -> List[int]:
    """Helper to generate temporary D4-D6 data for fuzz testing Quick Sort,

    independent of Ngan's implementation.
    """
    if n <= 0:
        return []
    rng = random.Random(seed)
    d1 = [rng.randrange(2**31) for _ in range(n)]

    if dataset == "D4":
        # Reversed sorted D1
        return sorted(d1, reverse=True)

    if dataset == "D5":
        # High duplicate values: sample K distinct keys
        k = rng.choice([2, 10, min(1000, max(1, n))])
        pool = [rng.randrange(2**31) for _ in range(k)]
        return [rng.choice(pool) for _ in range(n)]

    if dataset == "D6":
        # Concatenated sorted batches
        r = rng.choice([2, 16, 256])
        if r <= 0:
            r = 1
        # Split d1 into r batches, sort each, concatenate
        batch_size = math.ceil(n / r)
        result: List[int] = []
        for i in range(0, n, batch_size):
            batch = d1[i : i + batch_size]
            batch.sort()
            result.extend(batch)
        return result

    raise ValueError(f"Unknown mock dataset: {dataset}")


class QuickFixed(unittest.TestCase):
    """Mandatory fixed test cases specified by project proposal."""

    def test_fixed_cases(self) -> None:
        fixed_cases = [
            [],
            [7],
            [2, 1],
            [3, 3, 3],
            [0, 2147483647, 0],
        ]

        expected_keys = {
            "key_comparisons",
            "array_reads",
            "array_writes",
            "run_count",
            "avg_run_len",
        }

        for idx, original in enumerate(fixed_cases):
            with self.subTest(case_idx=idx, original=original):
                expected = sorted(original)

                # Test sort()
                arr_sort = list(original)
                quick.sort(arr_sort)
                self.assertEqual(
                    arr_sort,
                    expected,
                    f"sort() failed on fixed case {original}",
                )

                # Test sort_counted()
                arr_counted = list(original)
                metrics = quick.sort_counted(arr_counted)
                self.assertEqual(
                    arr_counted,
                    expected,
                    f"sort_counted() failed on fixed case {original}",
                )

                # Check same output between sort and sort_counted
                self.assertEqual(arr_sort, arr_counted)

                # Check metrics structure
                self.assertEqual(set(metrics.keys()), expected_keys)
                self.assertIsNone(metrics["run_count"])
                self.assertIsNone(metrics["avg_run_len"])
                self.assertIsInstance(metrics["key_comparisons"], int)
                self.assertIsInstance(metrics["array_reads"], int)
                self.assertIsInstance(metrics["array_writes"], int)
                self.assertGreaterEqual(metrics["key_comparisons"], 0)
                self.assertGreaterEqual(metrics["array_reads"], 0)
                self.assertGreaterEqual(metrics["array_writes"], 0)


class QuickFuzz(unittest.TestCase):
    """1,000 fuzz test cases covering lengths 0-200 and datasets D1-D6."""

    def test_1000_fuzz_cases(self) -> None:
        fuzz_seed = 203  # Fuzz test seed per project spec
        fuzz_rng = random.Random(fuzz_seed)

        datasets = ["D1", "D2", "D3", "D4", "D5", "D6"]

        for case_idx in range(1000):
            n = fuzz_rng.randint(0, 200)
            ds = fuzz_rng.choice(datasets)
            case_seed = fuzz_rng.randint(1, 1_000_000)

            # Generate input
            if ds in ("D1", "D2", "D3"):
                arr_in = generate(ds, n, case_seed)
            else:
                arr_in = _generate_mock_d4_to_d6(ds, n, case_seed)

            expected = sorted(arr_in)

            arr_sort = list(arr_in)
            quick.sort(arr_sort)

            arr_counted = list(arr_in)
            metrics = quick.sort_counted(arr_counted)

            # Verify correctness against sorted()
            self.assertEqual(
                arr_sort,
                expected,
                f"Fuzz case {case_idx} ({ds}, n={n}) sort() mismatch",
            )
            # Verify sort and sort_counted produce identical output
            self.assertEqual(
                arr_counted,
                arr_sort,
                f"Fuzz case {case_idx} ({ds}, n={n}) output mismatch between sort and sort_counted",
            )

            # Verify metrics
            self.assertIsNone(metrics["run_count"])
            self.assertIsNone(metrics["avg_run_len"])
            self.assertGreaterEqual(metrics["key_comparisons"], 0)
            self.assertGreaterEqual(metrics["array_reads"], 0)
            self.assertGreaterEqual(metrics["array_writes"], 0)


if __name__ == "__main__":
    unittest.main()
