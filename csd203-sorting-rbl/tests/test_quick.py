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


class QuickNganReview(unittest.TestCase):
    """Review by Ngan against the integrated generator, without mock D4-D6."""

    def test_plain_and_counted_make_same_comparison_decisions(self):
        class Key:
            trace = []

            def __init__(self, value, index):
                self.value, self.index = value, index

            def __lt__(self, other):
                Key.trace.append(("lt", self.index, other.index))
                return self.value < other.value

            def __gt__(self, other):
                Key.trace.append(("gt", self.index, other.index))
                return self.value > other.value

        rng = random.Random(203)
        for n in (0, 1, 2, 31, 64, 129, 1201):
            original = [Key(rng.randrange(31), i) for i in range(n)]
            a, b = list(original), list(original)
            Key.trace = []
            quick.sort(a)
            plain_trace = list(Key.trace)
            Key.trace = []
            stats = quick.sort_counted(b)
            with self.subTest(n=n):
                self.assertEqual(a, b)
                self.assertEqual(plain_trace, Key.trace)
                self.assertEqual(stats["key_comparisons"], len(Key.trace))
                self.assertEqual([x.value for x in a], sorted(x.value for x in original))

    def test_real_generator_all_dataset_parameters(self):
        families = [("D1", None, None), ("D2", None, None),
                    ("D3", None, None), ("D4", None, None),
                    ("D5", 1000, None), ("D5", 10, None), ("D5", 2, None),
                    ("D6", None, 2), ("D6", None, 16), ("D6", None, 256)]
        for seed in (2026, 2027, 2028):
            for ds, k, runs in families:
                with self.subTest(seed=seed, dataset=ds, k=k, runs=runs):
                    data = generate(ds, 1201, seed, k=k, runs=runs)
                    a, b = list(data), list(data)
                    quick.sort(a)
                    quick.sort_counted(b)
                    self.assertEqual(a, sorted(data))
                    self.assertEqual(b, a)

    def test_counts_match_observed_input_accesses_and_key_comparisons(self):
        class TrackedList(list):
            def __init__(self, values):
                super().__init__(values)
                self.reads = self.writes = 0

            def __getitem__(self, index):
                self.reads += 1
                return super().__getitem__(index)

            def __setitem__(self, index, value):
                self.writes += 1
                return super().__setitem__(index, value)

        class Key:
            comparisons = 0

            def __init__(self, value):
                self.value = value

            def __lt__(self, other):
                Key.comparisons += 1
                return self.value < other.value

            def __gt__(self, other):
                Key.comparisons += 1
                return self.value > other.value

        for values in ([2, 1], [3, 3, 3], [0, 2147483647, 0],
                       [5, 1, 6, 2, 10, 3]):
            a = TrackedList(Key(x) for x in values)
            Key.comparisons = 0
            stats = quick.sort_counted(a)
            self.assertEqual(stats["key_comparisons"], Key.comparisons)
            self.assertEqual(stats["array_reads"], a.reads)
            self.assertEqual(stats["array_writes"], a.writes)
            self.assertEqual([x.value for x in a], sorted(values))


if __name__ == "__main__":
    unittest.main()
