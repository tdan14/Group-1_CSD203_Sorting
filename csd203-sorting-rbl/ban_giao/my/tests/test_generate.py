"""Unit tests for dataset generator module (data/generate.py).

CSD203 RBL Sorting Research Project.
Author: My (D1-D3)
Reviewer: Ngan
"""

import math
import unittest

from data.generate import generate


class TestGenerate(unittest.TestCase):
    """Test suite for D1, D2, and D3 generation logic and boundary conditions."""

    def test_d1_validity_and_range(self) -> None:
        """Verify D1 size, domain [0, 2^31 - 1], and determinism."""
        n = 500
        seed = 2026
        d1_a = generate("D1", n, seed)
        d1_b = generate("D1", n, seed)

        self.assertEqual(len(d1_a), n)
        self.assertEqual(d1_a, d1_b, "D1 must be strictly deterministic with same seed")

        for val in d1_a:
            self.assertGreaterEqual(val, 0)
            self.assertLess(val, 2**31)

    def test_d2_is_sorted_d1(self) -> None:
        """Verify D2 equals sorted(D1) and is monotonically non-decreasing."""
        n = 500
        seed = 2027
        d1 = generate("D1", n, seed)
        d2 = generate("D2", n, seed)

        self.assertEqual(d2, sorted(d1))
        for i in range(len(d2) - 1):
            self.assertLessEqual(d2[i], d2[i + 1])

    def test_d3_swap_count_and_behavior(self) -> None:
        """Verify D3 starts from D2 and applies floor(n / 1000) swaps using seed+10000 stream."""
        seed = 2028

        # When n < 1000, swap count is 0 -> D3 must be identical to D2
        d2_small = generate("D2", 500, seed)
        d3_small = generate("D3", 500, seed)
        self.assertEqual(
            d3_small,
            d2_small,
            "When n < 1000, D3 must have 0 swaps and equal D2",
        )

        # When n = 1500, floor(1500 / 1000) = 1 swap -> at most 2 indices differ
        d2_1500 = generate("D2", 1500, seed)
        d3_1500 = generate("D3", 1500, seed)
        diff_indices = [
            i for i in range(1500) if d2_1500[i] != d3_1500[i]
        ]
        self.assertEqual(
            len(diff_indices),
            2,
            f"1 swap must change exactly 2 positions, got: {len(diff_indices)}",
        )

        # When n = 3000, floor(3000 / 1000) = 3 swaps -> at most 6 indices differ
        d2_3000 = generate("D2", 3000, seed)
        d3_3000 = generate("D3", 3000, seed)
        diff_3000 = [
            i for i in range(3000) if d2_3000[i] != d3_3000[i]
        ]
        self.assertLessEqual(
            len(diff_3000),
            6,
            "3 swaps must change at most 6 positions",
        )

    def test_official_and_fuzz_seeds(self) -> None:
        """Verify official seeds (2026, 2027, 2028) and fuzz seed (203) are reproducible."""
        for s in [2026, 2027, 2028, 203]:
            for ds in ["D1", "D2", "D3"]:
                run1 = generate(ds, 100, s)
                run2 = generate(ds, 100, s)
                self.assertEqual(
                    run1,
                    run2,
                    f"Dataset {ds} with seed {s} is not deterministic",
                )

    def test_boundary_n_zero_or_negative(self) -> None:
        """Verify boundary condition for n <= 0 returns empty list."""
        self.assertEqual(generate("D1", 0, 2026), [])
        self.assertEqual(generate("D2", 0, 2026), [])
        self.assertEqual(generate("D3", 0, 2026), [])
        self.assertEqual(generate("D1", -5, 2026), [])

    def test_d4_to_d6_stub(self) -> None:
        """Verify D4-D6 raise NotImplementedError as assigned to Ngan."""
        for ds in ["D4", "D5", "D6"]:
            with self.assertRaises(NotImplementedError):
                generate(ds, 10, 2026)

    def test_unknown_dataset(self) -> None:
        """Verify unknown dataset name raises ValueError."""
        with self.assertRaises(ValueError):
            generate("D99", 10, 2026)


if __name__ == "__main__":
    unittest.main()
