"""Benchmark Worker for CSD203 Sorting RBL.

Module: bench/worker.py
Authors: Hai, Thien (rq2-thien)
Project: CSD203 Sorting RBL

Executes a single sorting experiment trial in an isolated subprocess.
Supports:
- Modes: 'time', 'mem', 'count'
- Warm-up run on small dataset (N <= 1000)
- Oracle validation and output_check checksum calculation
- Error handling: ok, wrong, timeout, oom, crash
"""

import argparse
import importlib
import json
import os
import platform
import socket
import sys
import time
import tracemalloc
from typing import Any, Optional

from data.generate import (
    GENERATOR_VERSION,
    compute_input_sha256,
    compute_output_check,
    generate,
)

CSV_COLUMNS = [
    # 1. Identifier & Environment
    "run_id",
    "rq",
    "algorithm",
    "code_commit",
    "generator_version",
    "machine_id",
    "python_version",
    # 2. Input & Mode
    "dataset",
    "n",
    "k",
    "runs",
    "seed",
    "input_sha256",
    "mode",
    # 3. Status & Validation
    "status",
    "phase",
    "error_type",
    "output_check",
    "oracle_match",
    # 4. Measurement Results
    "elapsed_ms",
    "throughput_kps",
    "mem_peak_bytes",
    "key_comparisons",
    "array_reads",
    "array_writes",
    "run_count",
    "avg_run_len",
]


def get_git_commit() -> str:
    """Retrieves current git commit hash if available."""
    try:
        import subprocess
        res = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if res.returncode == 0:
            return res.stdout.strip()
    except Exception:
        pass
    return "workspace"


def get_machine_id() -> str:
    """Retrieves machine hostname or identifier."""
    return socket.gethostname() or "unknown_machine"


def get_algorithm_callable(algo_name: str, counted: bool = False):
    """Loads algorithm callable from src package."""
    algo_lower = algo_name.lower()
    if algo_lower == "lib-sorted":
        if counted:
            return None  # lib-sorted does not support counted mode
        return sorted

    # Map name to module
    module_map = {
        "radix": "src.radix",
        "heap": "src.heap",
        "quick": "src.quick",
        "merge": "src.merge",
        "timsort": "src.timsort",
        "timsort-noa": "src.timsort",
    }

    if algo_lower not in module_map:
        raise ValueError(f"Unknown algorithm: {algo_name}")

    mod_name = module_map[algo_lower]
    mod = importlib.import_module(mod_name)

    if algo_lower == "timsort-noa":
        func_name = "sort_noa_counted" if counted else "sort_noa"
    else:
        func_name = "sort_counted" if counted else "sort"

    if not hasattr(mod, func_name):
        raise AttributeError(f"Module {mod_name} does not provide {func_name}")

    return getattr(mod, func_name)


def run_trial(
    run_id: str,
    rq: str,
    algorithm: str,
    dataset: str,
    n: int,
    seed: int,
    mode: str,
    k: Optional[int] = None,
    runs: Optional[int] = None,
    code_commit: Optional[str] = None,
    machine_id: Optional[str] = None,
) -> dict[str, Any]:
    """Runs a single measurement trial and returns the full record dict."""
    if code_commit is None:
        code_commit = get_git_commit()
    if machine_id is None:
        machine_id = get_machine_id()

    record: dict[str, Any] = {col: "" for col in CSV_COLUMNS}
    record["run_id"] = run_id
    record["rq"] = rq
    record["algorithm"] = algorithm
    record["code_commit"] = code_commit
    record["generator_version"] = GENERATOR_VERSION
    record["machine_id"] = machine_id
    record["python_version"] = platform.python_version()
    record["dataset"] = dataset
    record["n"] = n
    record["k"] = k if k is not None else ""
    record["runs"] = runs if runs is not None else ""
    record["seed"] = seed
    record["mode"] = mode

    phase = "prepare"
    record["phase"] = phase

    try:
        # Phase 1: Prepare data
        data = generate(dataset=dataset, n=n, seed=seed, k=k, runs=runs)
        input_sha = compute_input_sha256(data)
        record["input_sha256"] = input_sha

        # Warm-up run on small data (N <= 1000)
        warmup_n = min(n, 1000)
        warmup_data = generate(dataset=dataset, n=warmup_n, seed=seed + 999, k=k, runs=runs)
        if algorithm.lower() == "lib-sorted":
            _ = sorted(warmup_data)
        else:
            warm_func = get_algorithm_callable(algorithm, counted=False)
            warm_func(warmup_data)

        # Working array for the actual trial
        work_arr = list(data)

        # Phase 2: Sorting execution
        phase = "sort"
        record["phase"] = phase

        elapsed_ms: Optional[float] = None
        mem_peak: Optional[int] = None
        count_stats: Optional[dict[str, Any]] = None

        if mode == "time":
            if algorithm.lower() == "lib-sorted":
                t0 = time.perf_counter_ns()
                sorted_result = sorted(work_arr)
                t1 = time.perf_counter_ns()
                work_arr = sorted_result
            else:
                sort_func = get_algorithm_callable(algorithm, counted=False)
                t0 = time.perf_counter_ns()
                sort_func(work_arr)
                t1 = time.perf_counter_ns()
            elapsed_ms = (t1 - t0) / 1_000_000.0

        elif mode == "mem":
            if algorithm.lower() == "lib-sorted":
                tracemalloc.start()
                sorted_result = sorted(work_arr)
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                work_arr = sorted_result
                mem_peak = peak
            else:
                sort_func = get_algorithm_callable(algorithm, counted=False)
                tracemalloc.start()
                sort_func(work_arr)
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                mem_peak = peak

        elif mode == "count":
            if algorithm.lower() == "lib-sorted":
                # lib-sorted does not support count mode
                work_arr = sorted(work_arr)
                count_stats = None
            else:
                sort_counted_func = get_algorithm_callable(algorithm, counted=True)
                count_stats = sort_counted_func(work_arr)
        else:
            raise ValueError(f"Unsupported measurement mode: {mode}")

        # Phase 3: Validate against oracle
        phase = "validate"
        record["phase"] = phase

        output_check = compute_output_check(work_arr)
        record["output_check"] = str(output_check)

        expected_oracle = sorted(data)
        is_match = (work_arr == expected_oracle)
        record["oracle_match"] = is_match

        if is_match:
            record["status"] = "ok"
            record["error_type"] = ""
        else:
            record["status"] = "wrong"
            record["error_type"] = "MismatchWithOracle"

        # Record measurement metrics
        if elapsed_ms is not None:
            record["elapsed_ms"] = f"{elapsed_ms:.4f}"
            if elapsed_ms > 0:
                record["throughput_kps"] = f"{(n / elapsed_ms):.4f}"

        if mem_peak is not None:
            record["mem_peak_bytes"] = str(mem_peak)

        if count_stats is not None:
            for k_stat in ("key_comparisons", "array_reads", "array_writes", "run_count", "avg_run_len"):
                val = count_stats.get(k_stat)
                record[k_stat] = "" if val is None else str(val)

    except MemoryError:
        record["status"] = "oom"
        record["error_type"] = "MemoryError"
    except Exception as exc:
        record["status"] = "crash"
        record["error_type"] = type(exc).__name__
        record["phase"] = phase

    return record


def main() -> None:
    parser = argparse.ArgumentParser(description="CSD203 Sorting Benchmark Worker")
    parser.add_argument("--run-id", type=str, default="run_dev")
    parser.add_argument("--rq", type=str, default="RQ2")
    parser.add_argument("--algo", type=str, required=True)
    parser.add_argument("--dataset", type=str, required=True)
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--mode", type=str, choices=["time", "mem", "count"], required=True)
    parser.add_argument("--k", type=int, default=None)
    parser.add_argument("--runs", type=int, default=None)
    parser.add_argument("--json", action="store_true", help="Output JSON instead of CSV line")

    args = parser.parse_args()

    res = run_trial(
        run_id=args.run_id,
        rq=args.rq,
        algorithm=args.algo,
        dataset=args.dataset,
        n=args.n,
        seed=args.seed,
        mode=args.mode,
        k=args.k,
        runs=args.runs,
    )

    if args.json:
        print(json.dumps(res))
    else:
        # Print CSV row formatted
        row_vals = [str(res[col]) for col in CSV_COLUMNS]
        print(",".join(row_vals))


if __name__ == "__main__":
    main()
