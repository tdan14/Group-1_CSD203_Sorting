"""Unit tests for the data generator (data/generate.py).

Module: tests/test_generate.py
Author: Hai (rq2-hai)
Project: CSD203 Sorting RBL

Checks every rule of the "Quy uoc generator" section of the group plan.
"""

import hashlib
import random
import struct
import unittest
from collections import Counter

from data.generate import (
    GENERATOR_VERSION,
    MAX_INT32,
    compute_input_sha256,
    compute_output_check,
    generate,
)

N = 20_000
SEED = 2026


class TestGenerator(unittest.TestCase):
    def test_reproducible(self) -> None:
        for ds, k, r in [("D1", None, None), ("D3", None, None), ("D5", 10, None), ("D6", None, 16)]:
            self.assertEqual(generate(ds, N, SEED, k=k, runs=r), generate(ds, N, SEED, k=k, runs=r))

    def test_domain(self) -> None:
        for ds, k, r in [("D1", None, None), ("D5", 1000, None), ("D6", None, 256)]:
            data = generate(ds, N, SEED, k=k, runs=r)
            self.assertEqual(len(data), N)
            self.assertTrue(all(0 <= x <= MAX_INT32 for x in data))

    def test_d2_d4(self) -> None:
        d1 = generate("D1", N, SEED)
        self.assertEqual(generate("D2", N, SEED), sorted(d1))
        self.assertEqual(generate("D4", N, SEED), sorted(d1, reverse=True))

    def test_d3_swaps_distinct_positions(self) -> None:
        d2 = generate("D2", N, SEED)
        d3 = generate("D3", N, SEED)
        self.assertEqual(sorted(d3), d2)  # same multiset
        # floor(N/1000) = 20 swaps of distinct positions -> at most 40 changed
        # positions, and at least 1 (with distinct random values, a swap of two
        # distinct positions always changes the array).
        changed = sum(1 for a, b in zip(d2, d3) if a != b)
        self.assertGreater(changed, 0)
        self.assertLessEqual(changed, 2 * (N // 1000))

    def test_d3_small_n_has_no_swaps(self) -> None:
        self.assertEqual(generate("D3", 999, SEED), generate("D2", 999, SEED))

    def test_d5_distinct_values(self) -> None:
        for k in (1000, 10, 2):
            data = generate("D5", N, SEED, k=k)
            self.assertEqual(len(set(data)), k)

    def test_d6_batches(self) -> None:
        for r in (2, 16, 256):
            d1 = generate("D1", N + 3, SEED)  # N+3: remainder is not zero
            d6 = generate("D6", N + 3, SEED, runs=r)
            base, rem = divmod(N + 3, r)
            pos = 0
            for i in range(r):
                ln = base + (1 if i < rem else 0)
                self.assertEqual(d6[pos:pos + ln], sorted(d1[pos:pos + ln]))
                pos += ln
            self.assertEqual(pos, N + 3)

    def test_d6_empty_batches_allowed(self) -> None:
        data = generate("D6", 5, SEED, runs=16)
        self.assertEqual(len(data), 5)

    def test_parameters_required(self) -> None:
        with self.assertRaises(ValueError):
            generate("D5", 10, SEED)
        with self.assertRaises(ValueError):
            generate("D6", 10, SEED)
        with self.assertRaises(ValueError):
            generate("D7", 10, SEED)

    def test_input_sha256_format(self) -> None:
        data = [0, 1, MAX_INT32, 256]
        expected = hashlib.sha256(struct.pack("<4I", *data)).hexdigest()
        self.assertEqual(compute_input_sha256(data), expected)

    def test_output_check_formula(self) -> None:
        h = 0
        for x in [3, 1, 2]:
            h = (31 * h + x) % (2 ** 64)
        self.assertEqual(compute_output_check([3, 1, 2]), h)

    def test_version(self) -> None:
        self.assertEqual(GENERATOR_VERSION, "1.1.0")


class TestGeneratorNganReview(unittest.TestCase):
    """D4-D6 acceptance by Ngan; generator 1.1.0 remains unchanged."""

    def test_d4_reverse_d2_across_seeds_and_boundaries(self):
        for seed in (203, 2026, 2027, 2028):
            for n in (0, 1, 2, 17, 1001):
                with self.subTest(seed=seed, n=n):
                    d1 = generate("D1", n, seed)
                    d4 = generate("D4", n, seed)
                    self.assertEqual(d4, list(reversed(generate("D2", n, seed))))
                    self.assertEqual(Counter(d4), Counter(d1))

    def test_d5_domain_repeatability_and_small_n_policy(self):
        # K describes the source pool, not a guarantee that every key occurs.
        for seed in (203, 2026, 2027, 2028):
            for k in (1000, 10, 2):
                for n in (0, 1, 7, 1001):
                    with self.subTest(seed=seed, k=k, n=n):
                        a = generate("D5", n, seed, k=k)
                        self.assertEqual(a, generate("D5", n, seed, k=k))
                        self.assertEqual(len(a), n)
                        self.assertLessEqual(len(set(a)), min(k, n))
                        self.assertTrue(all(type(x) is int and 0 <= x <= MAX_INT32
                                            for x in a))

    def test_d6_partition_sortedness_and_multiset_all_parameters(self):
        for seed in (203, 2026, 2027, 2028):
            for runs in (2, 16, 256):
                for n in (0, 1, 5, 257, 1003):
                    with self.subTest(seed=seed, runs=runs, n=n):
                        d1 = generate("D1", n, seed)
                        actual = generate("D6", n, seed, runs=runs)
                        self.assertEqual(actual, generate("D6", n, seed, runs=runs))
                        self.assertEqual(Counter(actual), Counter(d1))
                        # Balanced boundaries, including empty batches when R > N.
                        sizes = [n // runs + (i < n % runs) for i in range(runs)]
                        pos = 0
                        for size in sizes:
                            self.assertEqual(actual[pos:pos + size],
                                             sorted(d1[pos:pos + size]))
                            pos += size
                        self.assertEqual(pos, n)

    def test_local_rng_does_not_change_global_random_state(self):
        before = random.getstate()
        for ds, kwargs in (("D4", {}), ("D5", {"k": 10}),
                           ("D6", {"runs": 16})):
            generate(ds, 1001, 2026, **kwargs)
        self.assertEqual(random.getstate(), before)

    def test_d3_collision_regression_and_shared_validation(self):
        # Old handoff's D3 made a no-op at this seed; Lab already redraws.
        d2 = generate("D2", 1000, 2798)
        d3 = generate("D3", 1000, 2798)
        self.assertEqual(Counter(d3), Counter(d2))
        self.assertEqual(sum(a != b for a, b in zip(d2, d3)), 2)
        for ds, kwargs in (("D4", {}), ("D5", {"k": 2}),
                           ("D6", {"runs": 16})):
            with self.assertRaises(ValueError):
                generate(ds, -1, 2026, **kwargs)
        for ds, kwargs in (("D5", {"k": 0}), ("D6", {"runs": 0})):
            with self.assertRaises(ValueError):
                generate(ds, 10, 2026, **kwargs)


if __name__ == "__main__":
    unittest.main()
