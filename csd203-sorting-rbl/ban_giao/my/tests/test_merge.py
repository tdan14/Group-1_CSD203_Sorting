"""Unit, fuzz, and stability tests for Merge Sort module (src/merge.py).

CSD203 RBL Sorting Research Project.
Author: My (Review test harness for Ngan's Merge Sort)
Reviewer: Ngan

Note: Automatically skips if src/merge.py has not been delivered yet.
"""

import random
import unittest
from typing import List

try:
    import src.merge as merge
except ModuleNotFoundError:
    merge = None

from data.generate import generate
from tests.test_quick import _generate_mock_d4_to_d6


class Record:
    """Wrapper object with order tag to verify sorting stability.

    Only implements __lt__ based on key, without defining __eq__ or __le__.
    """

    __slots__ = ("key", "order")

    def __init__(self, key: int, order: int) -> None:
        self.key = key
        self.order = order

    def __lt__(self, other: "Record") -> bool:
        return self.key < other.key

    def __repr__(self) -> str:
        return f"Record(key={self.key}, order={self.order})"


@unittest.skipIf(merge is None, "src/merge.py chua duoc Ngan ban giao")
class MergeFixed(unittest.TestCase):
    """Mandatory fixed test cases for Merge Sort specified by project proposal."""

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
                merge.sort(arr_sort)
                self.assertEqual(
                    arr_sort,
                    expected,
                    f"sort() failed on fixed case {original}",
                )

                # Test sort_counted()
                arr_counted = list(original)
                metrics = merge.sort_counted(arr_counted)
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


@unittest.skipIf(merge is None, "src/merge.py chua duoc Ngan ban giao")
class MergeFuzz(unittest.TestCase):
    """1,000 fuzz test cases covering lengths 0-200 and datasets D1-D6."""

    def test_1000_fuzz_cases(self) -> None:
        fuzz_seed = 203  # Fuzz test seed per project spec
        fuzz_rng = random.Random(fuzz_seed)

        datasets = ["D1", "D2", "D3", "D4", "D5", "D6"]

        for case_idx in range(1000):
            n = fuzz_rng.randint(0, 200)
            ds = fuzz_rng.choice(datasets)
            case_seed = fuzz_rng.randint(1, 1_000_000)

            # Generate input (D1-D3 from generate, D4-D6 from test_quick mock)
            if ds in ("D1", "D2", "D3"):
                arr_in = generate(ds, n, case_seed)
            else:
                arr_in = _generate_mock_d4_to_d6(ds, n, case_seed)

            expected = sorted(arr_in)

            arr_sort = list(arr_in)
            merge.sort(arr_sort)

            arr_counted = list(arr_in)
            metrics = merge.sort_counted(arr_counted)

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


@unittest.skipIf(merge is None, "src/merge.py chua duoc Ngan ban giao")
class MergeStability(unittest.TestCase):
    """Stability verification on 1,000 records with duplicate keys."""

    def test_stability_on_1000_records(self) -> None:
        num_records = 1000
        # Create records where key repeats (e.g. key = i % 100), order preserves original index
        records: List[Record] = [
            Record(key=i % 100, order=i) for i in range(num_records)
        ]

        records_copy = list(records)
        merge.sort(records_copy)

        # 1. Verify keys are in non-decreasing order
        for i in range(len(records_copy) - 1):
            self.assertLessEqual(
                records_copy[i].key,
                records_copy[i + 1].key,
                "Keys are not sorted in ascending order",
            )

        # 2. Verify stability: for identical keys, original order must be strictly preserved
        for i in range(len(records_copy) - 1):
            if records_copy[i].key == records_copy[i + 1].key:
                self.assertLess(
                    records_copy[i].order,
                    records_copy[i + 1].order,
                    f"Stability violated for key {records_copy[i].key}: "
                    f"order {records_copy[i].order} appeared before {records_copy[i+1].order}",
                )


if __name__ == "__main__":
    unittest.main()
