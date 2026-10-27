"""Unit tests for the data generator (data/generate.py).

Module: tests/test_generate.py
Author: Hai (rq2-hai)
Project: CSD203 Sorting RBL

Checks every rule of the "Quy uoc generator" section of the group plan.
"""

import hashlib
import struct
import unittest

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


if __name__ == "__main__":
    unittest.main()
