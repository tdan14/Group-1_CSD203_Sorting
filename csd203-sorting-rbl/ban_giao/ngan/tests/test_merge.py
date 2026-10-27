"""Ngan's Merge tests: real D1-D6 generator, stability, and count parity.

Import failures are errors, never skipped: Merge is part of this delivery.
"""

import random
import unittest
from unittest.mock import patch

from data.generate import generate
from src import merge


FAMILIES = (
    ("D1", None, None), ("D2", None, None),
    ("D3", None, None), ("D4", None, None),
    ("D5", 1000, None), ("D5", 10, None), ("D5", 2, None),
    ("D6", None, 2), ("D6", None, 16), ("D6", None, 256),
)
METRICS = {"key_comparisons", "array_reads", "array_writes",
           "run_count", "avg_run_len"}


class Record:
    """Only < compares keys; identity and order distinguish equal keys."""

    __slots__ = ("key", "order", "trace")

    def __init__(self, key, order, trace=None):
        self.key, self.order, self.trace = key, order, trace

    def __lt__(self, other):
        if self.trace is not None:
            self.trace.append((self.order, other.order))
        return self.key < other.key


class TestMerge(unittest.TestCase):
    def check_both(self, original):
        expected = sorted(original)
        a, b = list(original), list(original)
        self.assertIsNone(merge.sort(a))
        stats = merge.sort_counted(b)
        self.assertEqual(a, expected)
        self.assertEqual(b, expected)
        self.assertEqual(set(stats), METRICS)
        for field in ("key_comparisons", "array_reads", "array_writes"):
            self.assertIs(type(stats[field]), int)
            self.assertGreaterEqual(stats[field], 0)
        self.assertIsNone(stats["run_count"])
        self.assertIsNone(stats["avg_run_len"])
        return stats

    def test_required_edge_cases(self):
        for a in ([], [7], [2, 1], [3, 3, 3], [0, 2147483647, 0]):
            with self.subTest(a=a):
                self.check_both(a)

    def test_1000_fuzz_cases_all_dataset_parameters(self):
        rng = random.Random(203)
        for case in range(1000):
            ds, k, runs = FAMILIES[case % len(FAMILIES)]
            n, seed = rng.randrange(201), rng.randrange(10**9)
            with self.subTest(case=case, dataset=ds, n=n, k=k, runs=runs):
                self.check_both(generate(ds, n, seed, k=k, runs=runs))

    def test_odd_lengths_and_larger_datasets(self):
        for n in (3, 31, 32, 33, 63, 64, 65, 257):
            self.check_both(list(range(n, 0, -1)))
        # Unlike fuzz inputs <= 200, D3 here actually performs swaps.
        for ds, k, runs in FAMILIES:
            with self.subTest(dataset=ds, k=k, runs=runs):
                self.check_both(generate(ds, 3001, 2026, k=k, runs=runs))

    def test_stability_1000_records_both_paths(self):
        rng = random.Random(203)
        for keys in ([5] * 1000, [rng.randrange(17) for _ in range(1000)],
                     [i // 10 for i in range(999, -1, -1)]):
            original = [Record(key, i) for i, key in enumerate(keys)]
            expected = sorted(original)  # key-only comparison; same object identities
            for sorter in (merge.sort, merge.sort_counted):
                with self.subTest(sorter=sorter.__name__):
                    actual = list(original)
                    sorter(actual)
                    self.assertEqual(actual, expected)

    def test_same_comparison_decisions_and_actual_comparison_count(self):
        keys = [4, 2, 4, 1, 3, 2, 0, 4, 1]
        normal_trace, counted_trace = [], []
        a = [Record(k, i, normal_trace) for i, k in enumerate(keys)]
        b = [Record(k, i, counted_trace) for i, k in enumerate(keys)]
        merge.sort(a)
        stats = merge.sort_counted(b)
        self.assertEqual(normal_trace, counted_trace)
        self.assertEqual(stats["key_comparisons"], len(counted_trace))
        self.assertEqual([x.order for x in a], [x.order for x in b])

    def test_exact_two_element_counts_and_trivial_inputs(self):
        # Two aux initializations + two copies into aux + two output writes.
        # Two input reads + two reads for comparison + one tail read.
        for a in ([2, 1], [1, 2], [3, 3]):
            stats = self.check_both(a)
            self.assertEqual(stats["key_comparisons"], 1)
            self.assertEqual(stats["array_reads"], 5)
            self.assertEqual(stats["array_writes"], 6)
        for a in ([], [7]):
            stats = self.check_both(a)
            self.assertEqual([stats[k] for k in ("key_comparisons", "array_reads",
                                                "array_writes")], [0, 0, 0])

    def test_aux_is_reused_and_input_has_no_slice_access(self):
        class NoSlices(list):
            def __getitem__(self, index):
                if isinstance(index, slice):
                    raise AssertionError("input slice allocated")
                return super().__getitem__(index)

            def __setitem__(self, index, value):
                if isinstance(index, slice):
                    raise AssertionError("input slice assignment")
                return super().__setitem__(index, value)

        for sorter, merge_name in ((merge.sort, "_merge"),
                                   (merge.sort_counted, "_merge_counted")):
            buffers = []
            original_merge = getattr(merge, merge_name)

            def observe(a, aux, *args):
                buffers.append(aux)
                return original_merge(a, aux, *args)

            a = NoSlices(range(32, -1, -1))
            with patch.object(merge, merge_name, side_effect=observe):
                sorter(a)
            self.assertEqual(a, list(range(33)))
            self.assertTrue(buffers)
            self.assertEqual(len(buffers[0]), len(a))
            self.assertTrue(all(aux is buffers[0] for aux in buffers))


if __name__ == "__main__":
    unittest.main()
