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
from data.generate import generate
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


class RadixNganReview(unittest.TestCase):
    """Output review by Ngan with integrated datasets and byte boundaries."""

    def test_real_generator_all_dataset_parameters(self):
        families = [("D1", None, None), ("D2", None, None),
                    ("D3", None, None), ("D4", None, None),
                    ("D5", 1000, None), ("D5", 10, None), ("D5", 2, None),
                    ("D6", None, 2), ("D6", None, 16), ("D6", None, 256)]
        for seed in (2026, 2027, 2028):
            for ds, k, runs in families:
                with self.subTest(seed=seed, dataset=ds, k=k, runs=runs):
                    original = generate(ds, 1201, seed, k=k, runs=runs)
                    a, b = list(original), list(original)
                    self.assertIsNone(radix.sort(a))
                    radix.sort_counted(b)
                    self.assertEqual(a, sorted(original))
                    self.assertEqual(b, a)

    def test_boundaries_of_all_four_bytes(self):
        original = [2147483647, 16777216, 16777215, 65536, 65535,
                    256, 255, 1, 0, 256, 65536, 16777216]
        for sorter in (radix.sort, radix.sort_counted):
            with self.subTest(sorter=sorter.__name__):
                a = list(original)
                sorter(a)
                self.assertEqual(a, sorted(original))

    def test_counted_matches_observed_normal_array_operations(self):
        """Observe the normal path independently, including buffers and copy-back.

        This is logical element traffic, not internal CPython memory accesses.
        Only buffer construction is instrumented in an in-memory AST copy;
        the checked-in algorithm and the measured path are unchanged.
        """
        import ast
        import inspect
        import textwrap

        totals = {"reads": 0, "writes": 0}

        class ObservedList(list):
            def __init__(self, values, initialize=True):
                super().__init__(values)
                if initialize:
                    totals["writes"] += len(self)

            def __iter__(self):
                for value in list.__iter__(self):
                    totals["reads"] += 1
                    yield value

            def __getitem__(self, index):
                totals["reads"] += (len(range(*index.indices(len(self))))
                                    if isinstance(index, slice) else 1)
                return list.__getitem__(self, index)

            def __setitem__(self, index, value):
                if isinstance(index, slice):
                    # list slice assignment reads the RHS buffer internally.
                    totals["reads"] += len(value)
                    totals["writes"] += len(value)
                    # Avoid counting that same copy again through __iter__.
                    value = list(list.__iter__(value))
                else:
                    totals["writes"] += 1
                return list.__setitem__(self, index, value)

        class WrapBuffers(ast.NodeTransformer):
            def visit_Assign(self, node):
                self.generic_visit(node)
                if (isinstance(node.value, ast.BinOp)
                        and isinstance(node.value.op, ast.Mult)
                        and isinstance(node.value.left, ast.List)):
                    node.value = ast.Call(func=ast.Name(id="ObservedList", ctx=ast.Load()),
                                          args=[node.value], keywords=[])
                return node

        tree = ast.parse(textwrap.dedent(inspect.getsource(radix.sort)))
        tree = ast.fix_missing_locations(WrapBuffers().visit(tree))
        namespace = {"ObservedList": ObservedList}
        exec(compile(tree, "<observed radix sort>", "exec"), namespace)
        cases = [[], [7], [2, 1], [3] * 10, [0, MAX_INT32, 256, 65536]]
        cases += [generate(ds, 1001, 2026, **kw) for ds, kw in
                  (("D1", {}), ("D3", {}), ("D5", {"k": 2}),
                   ("D6", {"runs": 16}))]
        for original in cases:
            with self.subTest(n=len(original)):
                totals.update(reads=0, writes=0)
                observed = ObservedList(original, initialize=False)
                namespace["sort"](observed)
                measured = dict(totals)
                counted = list(original)
                stats = radix.sort_counted(counted)
                self.assertEqual(observed, sorted(original))
                self.assertEqual(counted, observed)
                self.assertEqual(stats["array_reads"], measured["reads"])
                self.assertEqual(stats["array_writes"], measured["writes"])


if __name__ == "__main__":
    unittest.main()
