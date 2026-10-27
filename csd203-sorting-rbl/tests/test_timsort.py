"""Kiem tra rieng phan Timsort va noA cua Dan."""
import random
import unittest
from unittest.mock import patch

from data.generate import generate
from src import timsort


class Record:
    comparisons = []

    def __init__(self, key, order):
        self.key = key
        self.order = order

    def __lt__(self, other):
        Record.comparisons.append((self.order, other.order))
        return self.key < other.key


def record_key(record):
    return record.key


class BufferList(list):
    def __init__(self, values):
        super().__init__(values)
        self.buffer_sizes = []

    def __getitem__(self, index):
        result = super().__getitem__(index)
        if isinstance(index, slice):
            self.buffer_sizes.append(len(result))
        return result


class TimsortTests(unittest.TestCase):
    def test_minrun_boundaries(self):
        cases = [(0, 0), (1, 1), (31, 31), (32, 32), (63, 63),
                 (64, 32), (65, 33), (127, 64), (128, 32), (129, 33)]
        for n, expected in cases:
            self.assertEqual(timsort.minrun_length(n), expected)

    def test_power_matches_midpoint_definition(self):
        rng = random.Random(203)
        for case in range(1000):
            total = rng.randint(2, 10000)
            start = rng.randint(0, total - 2)
            left_size = rng.randint(1, total - start - 1)
            right_size = rng.randint(1, total - start - left_size)
            left_midpoint = 2 * start + left_size
            right_midpoint = left_midpoint + left_size + right_size
            expected = 1
            while True:
                scale = 2 ** expected
                left_node = left_midpoint * scale // (2 * total)
                right_node = right_midpoint * scale // (2 * total)
                if left_node != right_node:
                    break
                expected += 1
            actual = timsort.node_power(start, left_size, right_size, total)
            self.assertEqual(actual, expected)

    def test_four_entry_points_on_edges_and_1000_datasets(self):
        functions = [timsort.sort, timsort.sort_counted,
                     timsort.sort_noa, timsort.sort_noa_counted]
        inputs = [[], [7], [2, 1], [3, 3, 3], [0, 2147483647, 0]]
        rng = random.Random(203)
        configurations = [("D1", None, None), ("D2", None, None),
                          ("D3", None, None), ("D4", None, None),
                          ("D5", 1000, None), ("D5", 10, None), ("D5", 2, None),
                          ("D6", None, 2), ("D6", None, 16), ("D6", None, 256)]
        for case in range(1000):
            dataset, k, runs = configurations[case % len(configurations)]
            n = rng.randrange(201)
            inputs.append(generate(dataset, n, rng.randrange(2 ** 31), k=k, runs=runs))
        for original in inputs:
            expected = sorted(original)
            for function in functions:
                values = original.copy()
                function(values)
                self.assertEqual(values, expected)

    def test_stability_and_exact_comparison_sequence(self):
        rng = random.Random(203)
        for size in [0, 1, 2, 31, 32, 63, 64, 65, 127, 128, 129, 1000]:
            original = []
            for index in range(size):
                original.append(Record(rng.randrange(13), index))
            expected = sorted(original, key=record_key)
            for plain, counted in [(timsort.sort, timsort.sort_counted),
                                   (timsort.sort_noa, timsort.sort_noa_counted)]:
                values = original.copy()
                Record.comparisons = []
                plain(values)
                sequence = Record.comparisons.copy()
                self.assertEqual(values, expected)

                values = original.copy()
                Record.comparisons = []
                metrics = counted(values)
                self.assertEqual(values, expected)
                self.assertEqual(Record.comparisons, sequence)
                self.assertEqual(metrics["key_comparisons"], len(sequence))

    def test_merge_is_stable_and_copies_only_shorter_run(self):
        for left_size, right_size in [(5, 9), (9, 5), (7, 7)]:
            original = []
            for index in range(left_size):
                original.append(Record(index // 2, index))
            for index in range(right_size):
                original.append(Record(index // 2, left_size + index))
            expected = sorted(original, key=record_key)
            for counted in [False, True]:
                values = BufferList(original)
                if counted:
                    timsort._merge_counted(values, 0, left_size, len(values),
                                           {"key_comparisons": 0})
                else:
                    timsort._merge(values, 0, left_size, len(values))
                self.assertEqual(values, expected)
                self.assertEqual(values.buffer_sizes, [min(left_size, right_size)])

    def test_strict_descending_and_equal_boundary(self):
        values = [Record(5, 0), Record(4, 1), Record(4, 2), Record(3, 3)]
        self.assertEqual(timsort._count_run(values, 0, len(values)), 2)
        self.assertEqual(values[0].order, 1)
        self.assertEqual(values[1].order, 0)
        for function in [timsort.sort, timsort.sort_counted,
                         timsort.sort_noa, timsort.sort_noa_counted]:
            original = [Record(5, 0), Record(4, 1), Record(4, 2), Record(3, 3)]
            expected = sorted(original, key=record_key)
            function(original)
            self.assertEqual(original, expected)

    def test_natural_run_metrics_and_noa_does_not_detect_runs(self):
        inputs = [list(range(1000)), list(range(999, -1, -1)), [7] * 1000]
        for original in inputs:
            metrics = timsort.sort_counted(original.copy())
            self.assertEqual(metrics["key_comparisons"], 999)
            self.assertEqual(metrics["run_count"], 1)
            self.assertEqual(metrics["avg_run_len"], 1000)
        with patch.object(timsort, "_count_run", side_effect=AssertionError), \
             patch.object(timsort, "_count_run_counted", side_effect=AssertionError):
            values = list(range(1000, -1, -1))
            timsort.sort_noa(values)
            self.assertEqual(values, list(range(1001)))
            metrics = timsort.sort_noa_counted(values)
            self.assertIsNone(metrics["run_count"])
            self.assertIsNone(metrics["avg_run_len"])

    def test_powersort_merges_deeper_boundary_first(self):
        merges = []

        def record_merge(values, start, middle, end):
            merges.append((start, middle, end))

        stack = []
        timsort._push_run([], stack, 0, 64, 384, record_merge)
        timsort._push_run([], stack, 64, 64, 384, record_merge)
        self.assertEqual(merges, [])
        timsort._push_run([], stack, 128, 256, 384, record_merge)
        self.assertEqual(merges, [(0, 64, 128)])
        timsort._finish_merges([], stack, record_merge)
        self.assertEqual(merges, [(0, 64, 128), (0, 128, 384)])
        self.assertEqual(stack[0][1], 384)


if __name__ == "__main__":
    unittest.main()
