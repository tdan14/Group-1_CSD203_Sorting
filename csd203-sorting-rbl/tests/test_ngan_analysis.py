"""Corruption tests for the CSV audit used by Ngan's manuscript."""
import contextlib
import csv
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from bench.worker import CSV_COLUMNS, run_trial
from scripts.analyze_ngan import ROOT, audit


class NganAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.raw, self.config, self.env = [root / n for n in ("raw.csv", "config.json", "env.json")]
        configs = [dict(run_id="audit-test", rq="RQ1", algo="radix", dataset="D1",
                        n=5, seed=s, mode="count") for s in (2026, 2027, 2028)]
        self.config.write_text(json.dumps(configs), encoding="utf-8")
        with contextlib.redirect_stderr(io.StringIO()):
            self.rows = [run_trial(c["run_id"], c["rq"], c["algo"], c["dataset"], c["n"],
                                   c["seed"], c["mode"], code_commit="abc1234", machine_id="audit-test")
                         for c in configs]
        self.environment = dict(source_commit="abc1234567890", machine_id="audit-test",
                                python_version=self.rows[0]["python_version"],
                                source_files_sha256={"src/radix.py": hashlib.sha256(
                                    (ROOT / "src/radix.py").read_bytes()).hexdigest()})
        self.env.write_text(json.dumps(self.environment), encoding="utf-8")
        self.write_rows()

    def write_rows(self):
        with self.raw.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            writer.writerows(self.rows)

    def inspect(self):
        return audit(self.raw, self.config, self.env)

    def test_real_tiny_run_is_validated(self):
        rows, summary, checked = self.inspect()
        self.assertEqual(checked["statuses"], {"ok": 3})
        self.assertEqual(checked["regenerated_inputs"], 3)
        self.assertTrue(summary[0]["complete"])

    def test_rejects_missing_and_duplicated_trials(self):
        saved = list(self.rows)
        for corrupted in (saved[:2], saved + [saved[0]]):
            self.rows = corrupted
            self.write_rows()
            with self.assertRaises(ValueError):
                self.inspect()

    def test_rejects_tampered_hash_oracle_counts_and_environment(self):
        for field, value in (("input_sha256", "bad"), ("output_check", "0"),
                             ("oracle_match", False), ("array_reads", "1"),
                             ("machine_id", "other"), ("code_commit", "other")):
            old = self.rows[0][field]
            self.rows[0][field] = value
            self.write_rows()
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.inspect()
            self.rows[0][field] = old

    def test_failure_is_retained_and_group_not_complete(self):
        self.rows[2].update(status="timeout", phase="sort", oracle_match=False,
                            input_sha256="", output_check="")
        self.write_rows()
        rows, summary, checked = self.inspect()
        self.assertEqual(len(rows), 3)
        self.assertEqual(summary[0]["n_ok"], 2)
        self.assertFalse(summary[0]["complete"])
        self.assertEqual(checked["statuses"], {"ok": 2, "timeout": 1})

    def test_rejects_changed_source_manifest(self):
        self.environment["source_files_sha256"]["src/radix.py"] = "bad"
        self.env.write_text(json.dumps(self.environment), encoding="utf-8")
        with self.assertRaises(ValueError):
            self.inspect()

    def test_rejects_changed_raw_csv_after_manifest_is_finalized(self):
        self.environment["raw_csv_sha256"] = hashlib.sha256(self.raw.read_bytes()).hexdigest()
        self.env.write_text(json.dumps(self.environment), encoding="utf-8")
        self.inspect()
        self.rows[0]["array_reads"] += "0"
        self.write_rows()
        with self.assertRaises(ValueError):
            self.inspect()


if __name__ == "__main__":
    unittest.main()
