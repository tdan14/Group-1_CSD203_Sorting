"""Benchmark Runner for CSD203 Sorting RBL.

Module: bench/runner.py
Authors: Hai, Thien (rq2-thien)
Project: CSD203 Sorting RBL

Coordinates multi-process execution of sorting trials using subprocess.run with timeout=60s.
Features:
- Subprocess isolation per trial
- Enforces 60-second timeout
- Handles and logs status: ok, wrong, timeout, oom, crash
- Saves results directly to UTF-8 CSV with standardized schema
- Supports filtering by RQ, algorithm, dataset, N, mode
"""

import argparse
import csv
import json
import os
import subprocess
import sys
import time
from typing import Any, Optional

from bench.worker import CSV_COLUMNS


def run_single_subprocess_trial(
    run_id: str,
    rq: str,
    algo: str,
    dataset: str,
    n: int,
    seed: int,
    mode: str,
    k: Optional[int] = None,
    runs: Optional[int] = None,
    timeout: float = 60.0,
) -> dict[str, Any]:
    """Spawns an isolated subprocess running bench.worker and captures output."""
    cmd = [
        sys.executable,
        "-m",
        "bench.worker",
        "--run-id",
        run_id,
        "--rq",
        rq,
        "--algo",
        algo,
        "--dataset",
        dataset,
        "--n",
        str(n),
        "--seed",
        str(seed),
        "--mode",
        mode,
        "--json",
    ]
    if k is not None:
        cmd.extend(["--k", str(k)])
    if runs is not None:
        cmd.extend(["--runs", str(runs)])

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if proc.returncode == 0 and proc.stdout.strip():
            # Parse JSON line from worker
            try:
                line = proc.stdout.strip().splitlines()[-1]
                return json.loads(line)
            except Exception as e:
                return _build_error_record(
                    run_id, rq, algo, dataset, n, seed, mode, k, runs,
                    status="crash", error_type=f"JSONDecodeError: {str(e)}", phase="validate"
                )
        else:
            stderr = proc.stderr.strip()
            err_type = "ProcessCrash"
            status = "crash"
            if "MemoryError" in stderr:
                status = "oom"
                err_type = "MemoryError"
            elif "RecursionError" in stderr:
                status = "crash"
                err_type = "RecursionError"

            return _build_error_record(
                run_id, rq, algo, dataset, n, seed, mode, k, runs,
                status=status, error_type=err_type, phase="sort"
            )

    except subprocess.TimeoutExpired:
        return _build_error_record(
            run_id, rq, algo, dataset, n, seed, mode, k, runs,
            status="timeout", error_type="TimeoutExpired", phase="sort"
        )
    except Exception as exc:
        return _build_error_record(
            run_id, rq, algo, dataset, n, seed, mode, k, runs,
            status="crash", error_type=type(exc).__name__, phase="prepare"
        )


def _build_error_record(
    run_id: str,
    rq: str,
    algo: str,
    dataset: str,
    n: int,
    seed: int,
    mode: str,
    k: Optional[int],
    runs: Optional[int],
    status: str,
    error_type: str,
    phase: str,
) -> dict[str, Any]:
    """Constructs a standardized record when a trial fails or times out."""
    rec = {col: "" for col in CSV_COLUMNS}
    rec["run_id"] = run_id
    rec["rq"] = rq
    rec["algorithm"] = algo
    rec["dataset"] = dataset
    rec["n"] = n
    rec["seed"] = seed
    rec["mode"] = mode
    rec["k"] = k if k is not None else ""
    rec["runs"] = runs if runs is not None else ""
    rec["status"] = status
    rec["error_type"] = error_type
    rec["phase"] = phase
    rec["oracle_match"] = False
    return rec


def execute_matrix(
    configs: list[dict[str, Any]],
    output_csv_path: str,
    timeout: float = 60.0,
) -> None:
    """Executes a list of trial configurations sequentially and writes to CSV."""
    os.makedirs(os.path.dirname(os.path.abspath(output_csv_path)), exist_ok=True)
    file_exists = os.path.exists(output_csv_path)

    with open(output_csv_path, mode="a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        if not file_exists:
            writer.writeheader()
            f.flush()

        total = len(configs)
        for idx, cfg in enumerate(configs, 1):
            print(
                f"[{idx}/{total}] Running: algo={cfg['algo']}, dataset={cfg['dataset']}, "
                f"n={cfg['n']}, seed={cfg['seed']}, mode={cfg['mode']} ... ",
                end="",
                flush=True,
            )
            rec = run_single_subprocess_trial(
                run_id=cfg.get("run_id", "run_main"),
                rq=cfg.get("rq", "RQ2"),
                algo=cfg["algo"],
                dataset=cfg["dataset"],
                n=cfg["n"],
                seed=cfg["seed"],
                mode=cfg["mode"],
                k=cfg.get("k"),
                runs=cfg.get("runs"),
                timeout=timeout,
            )
            writer.writerow(rec)
            f.flush()
            print(f"status={rec['status']} (elapsed={rec['elapsed_ms']}ms, mem={rec['mem_peak_bytes']}B)")


def main() -> None:
    parser = argparse.ArgumentParser(description="CSD203 Sorting Benchmark Runner")
    parser.add_argument("--config", type=str, help="Path to JSON configuration file")
    parser.add_argument("--out", type=str, default="results/raw/output.csv", help="Output CSV path")
    parser.add_argument("--timeout", type=float, default=60.0, help="Timeout in seconds")
    parser.add_argument("--pilot", action="store_true", help="Run a quick pilot test")

    args = parser.parse_args()

    if args.pilot:
        print("Running quick pilot benchmark for Radix and lib-sorted...")
        pilot_configs = []
        for algo in ["radix", "lib-sorted"]:
            for mode in ["time", "mem", "count"]:
                if algo == "lib-sorted" and mode == "count":
                    continue
                pilot_configs.append({
                    "run_id": "run_pilot",
                    "rq": "RQ2",
                    "algo": algo,
                    "dataset": "D1",
                    "n": 10000,
                    "seed": 2026,
                    "mode": mode,
                })
        execute_matrix(pilot_configs, args.out, timeout=args.timeout)
    elif args.config:
        with open(args.config, "r", encoding="utf-8") as f:
            cfgs = json.load(f)
        execute_matrix(cfgs, args.out, timeout=args.timeout)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
