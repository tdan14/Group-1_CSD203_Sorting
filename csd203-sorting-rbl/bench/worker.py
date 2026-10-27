"""Benchmark Worker for CSD203 Sorting RBL.

Module: bench/worker.py
Authors: Hai, Thien (rq2-thien)
Project: CSD203 Sorting RBL

Executes a single measurement trial (one algorithm x dataset x seed x mode)
inside its own process. The runner starts one worker per trial.

Protocol:
1. prepare  : generate data, input_sha256, warm-up on N <= 1000, copy input.
2. sort     : the ONLY measured region (time / mem / count).
3. validate : output_check, full comparison with sorted(data).

Phase markers ("PHASE:<name>") are written to stderr and flushed at every
phase change. If the process is killed by the runner's 60 s timeout or dies
abruptly, the runner reads the last marker to know whether the algorithm
had started ("sort") or not ("prepare"), as required by the group plan.
Nothing is printed inside the measured region.
"""

import argparse
import importlib
import json
import platform
import socket
import subprocess
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

# Official algorithm names used in the CSV (group plan).
ALGORITHMS = ("quick", "merge", "heap", "radix", "timsort", "timsort-noA", "lib-sorted")

# algorithm name -> (module, sort function, counted function)
_ALGO_TABLE = {
    "quick": ("src.quick", "sort", "sort_counted"),
    "merge": ("src.merge", "sort", "sort_counted"),
    "heap": ("src.heap", "sort", "sort_counted"),
    "radix": ("src.radix", "sort", "sort_counted"),
    "timsort": ("src.timsort", "sort", "sort_counted"),
    # timsort-noA lives in the same module (shared minrun/merge/Powersort code).
    # Function names agreed with Dan: sort_noa / sort_noa_counted.
    "timsort-noa": ("src.timsort", "sort_noa", "sort_noa_counted"),
}

COUNT_FIELDS = ("key_comparisons", "array_reads", "array_writes", "run_count", "avg_run_len")


def mark_phase(phase: str) -> None:
    """Writes a phase marker to stderr so the runner can recover it on timeout."""
    print(f"PHASE:{phase}", file=sys.stderr, flush=True)


def canonical_algorithm(name: str) -> str:
    """Maps any capitalisation to the official CSV name (e.g. 'timsort-noa' -> 'timsort-noA')."""
    for official in ALGORITHMS:
        if official.lower() == name.lower():
            return official
    raise ValueError(f"Unknown algorithm: {name}")


def get_git_commit() -> str:
    """Returns the short git commit hash, with '-dirty' if there are uncommitted changes."""
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        if res.returncode != 0:
            return "workspace"
        commit = res.stdout.strip()
        dirty = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"],
            capture_output=True, text=True, timeout=5,
        )
        if dirty.returncode == 0 and dirty.stdout.strip():
            commit += "-dirty"
        return commit
    except Exception:
        return "workspace"


def get_machine_id() -> str:
    """Returns the machine hostname."""
    return socket.gethostname() or "unknown_machine"


def get_algorithm_callable(algo_name: str, counted: bool = False):
    """Loads the sort (or counted sort) function of an algorithm."""
    key = algo_name.lower()
    if key == "lib-sorted":
        if counted:
            raise ValueError("lib-sorted does not support count mode")
        return sorted
    if key not in _ALGO_TABLE:
        raise ValueError(f"Unknown algorithm: {algo_name}")
    mod_name, fn_sort, fn_counted = _ALGO_TABLE[key]
    mod = importlib.import_module(mod_name)
    func_name = fn_counted if counted else fn_sort
    if not hasattr(mod, func_name):
        raise AttributeError(f"Module {mod_name} does not provide {func_name}")
    return getattr(mod, func_name)


def base_record(
    run_id: str, rq: str, algorithm: str, dataset: str, n: int, seed: int, mode: str,
    k: Optional[int], runs: Optional[int],
    code_commit: str, machine_id: str,
) -> dict[str, Any]:
    """Builds a record with identification fields filled and results empty."""
    record: dict[str, Any] = {col: "" for col in CSV_COLUMNS}
    record.update({
        "run_id": run_id,
        "rq": rq,
        "algorithm": algorithm,
        "code_commit": code_commit,
        "generator_version": GENERATOR_VERSION,
        "machine_id": machine_id,
        "python_version": platform.python_version(),
        "dataset": dataset.upper(),
        "n": n,
        "k": k if k is not None else "",
        "runs": runs if runs is not None else "",
        "seed": seed,
        "mode": mode,
    })
    return record


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
    """Runs one measurement trial and returns the full CSV record."""
    if code_commit is None:
        code_commit = get_git_commit()
    if machine_id is None:
        machine_id = get_machine_id()

    phase = "prepare"
    mark_phase(phase)
    try:
        algorithm = canonical_algorithm(algorithm)
    except ValueError as exc:
        rec = base_record(run_id, rq, algorithm, dataset, n, seed, mode, k, runs, code_commit, machine_id)
        rec.update(status="crash", phase=phase, error_type="UnknownAlgorithm", oracle_match=False)
        print(str(exc), file=sys.stderr)
        return rec

    record = base_record(run_id, rq, algorithm, dataset, n, seed, mode, k, runs, code_commit, machine_id)
    record["phase"] = phase
    is_lib = algorithm == "lib-sorted"

    try:
        if mode not in ("time", "mem", "count"):
            raise ValueError(f"Unsupported measurement mode: {mode}")
        if is_lib and mode == "count":
            # Group plan: lib-sorted is measured in time/mem only; count fields stay empty.
            raise ValueError("lib-sorted does not support count mode")

        # ---- Phase 1: prepare (outside the measured region) ----
        data = generate(dataset=dataset, n=n, seed=seed, k=k, runs=runs)
        record["input_sha256"] = compute_input_sha256(data)

        sort_func = get_algorithm_callable(algorithm, counted=(mode == "count"))

        # Warm-up once on the same dataset family, N <= 1000, result discarded.
        warmup_data = generate(dataset=dataset, n=min(n, 1000), seed=seed + 999, k=k, runs=runs)
        if is_lib:
            _ = sorted(warmup_data)
        else:
            get_algorithm_callable(algorithm, counted=False)(warmup_data)
        del warmup_data

        work_arr = list(data)  # fresh copy: every algorithm sees the same input

        # ---- Phase 2: sort (measured region) ----
        phase = "sort"
        record["phase"] = phase
        mark_phase(phase)

        elapsed_ms: Optional[float] = None
        mem_peak: Optional[int] = None
        count_stats: Optional[dict[str, Any]] = None

        if mode == "time":
            if is_lib:
                t0 = time.perf_counter_ns()
                result = sorted(work_arr)  # returned list is the result; not copied back
                t1 = time.perf_counter_ns()
                work_arr = result
            else:
                t0 = time.perf_counter_ns()
                sort_func(work_arr)
                t1 = time.perf_counter_ns()
            elapsed_ms = (t1 - t0) / 1_000_000.0

        elif mode == "mem":
            if is_lib:
                tracemalloc.start()
                result = sorted(work_arr)
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                work_arr = result
            else:
                tracemalloc.start()
                sort_func(work_arr)
                _, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
            mem_peak = peak

        else:  # count
            count_stats = sort_func(work_arr)

        # ---- Phase 3: validate (outside the measured region, tracing already off) ----
        phase = "validate"
        record["phase"] = phase
        mark_phase(phase)

        record["output_check"] = str(compute_output_check(work_arr))
        is_match = work_arr == sorted(data)
        record["oracle_match"] = is_match
        if is_match:
            record["status"] = "ok"
            record["error_type"] = ""
        else:
            record["status"] = "wrong"
            record["error_type"] = "MismatchWithOracle"

        if elapsed_ms is not None:
            record["elapsed_ms"] = f"{elapsed_ms:.4f}"
            if elapsed_ms > 0:
                # N / elapsed_ms = thousand elements per second
                record["throughput_kps"] = f"{(n / elapsed_ms):.4f}"
        if mem_peak is not None:
            record["mem_peak_bytes"] = str(mem_peak)
        if count_stats is not None:
            for field in COUNT_FIELDS:
                val = count_stats.get(field)
                record[field] = "" if val is None else str(val)

    except MemoryError:
        if tracemalloc.is_tracing():
            tracemalloc.stop()
        record["status"] = "oom"
        record["error_type"] = "MemoryError"
        record["phase"] = phase
        record["oracle_match"] = False
    except Exception as exc:
        if tracemalloc.is_tracing():
            tracemalloc.stop()
        record["status"] = "crash"
        record["error_type"] = type(exc).__name__
        record["phase"] = phase
        record["oracle_match"] = False
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)

    return record


def main() -> None:
    parser = argparse.ArgumentParser(description="CSD203 Sorting Benchmark Worker (one trial)")
    parser.add_argument("--run-id", type=str, default="run_dev")
    parser.add_argument("--rq", type=str, default="RQ2")
    parser.add_argument("--algo", type=str, required=True)
    parser.add_argument("--dataset", type=str, required=True)
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--mode", type=str, choices=["time", "mem", "count"], required=True)
    parser.add_argument("--k", type=int, default=None)
    parser.add_argument("--runs", type=int, default=None)
    parser.add_argument("--code-commit", type=str, default=None,
                        help="Passed by the runner so all rows of one run share the same commit")
    parser.add_argument("--json", action="store_true", help="Print a JSON record instead of a CSV line")
    args = parser.parse_args()

    res = run_trial(
        run_id=args.run_id, rq=args.rq, algorithm=args.algo, dataset=args.dataset,
        n=args.n, seed=args.seed, mode=args.mode, k=args.k, runs=args.runs,
        code_commit=args.code_commit,
    )

    if args.json:
        print(json.dumps(res), flush=True)
    else:
        print(",".join(str(res[col]) for col in CSV_COLUMNS), flush=True)


if __name__ == "__main__":
    main()
