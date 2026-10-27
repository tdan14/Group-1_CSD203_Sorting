"""Benchmark Runner for CSD203 Sorting RBL.

Module: bench/runner.py
Authors: Hai, Thien (rq2-thien)
Project: CSD203 Sorting RBL

Runs trials sequentially, one subprocess per trial (subprocess.run, timeout 60 s),
and appends one CSV row per trial.

Features:
- Status: ok, wrong, timeout, oom, crash (oom only when a MemoryError is seen;
  a process killed by a signal is recorded as crash, never guessed as oom).
- Phase recovery: on timeout/crash the last "PHASE:<name>" marker printed by
  the worker tells whether the algorithm had started (sort) or not (prepare).
- Every row, including failed ones, carries code_commit, machine_id,
  python_version and generator_version.
- Filters: --rq, --algo, --dataset, --n, --mode, --seed.
- --resume: skips trials already present in the output CSV for the same
  code_commit and machine_id (useful when a long run is interrupted).
- Warns when the interpreter is not the agreed CPython 3.12;
  --strict-python turns the warning into an error (use it for official runs).
"""

import argparse
import csv
import json
import os
import platform
import re
import subprocess
import sys
import time
from typing import Any, Optional

from bench.worker import CSV_COLUMNS, canonical_algorithm, get_git_commit, get_machine_id
from data.generate import GENERATOR_VERSION

EXPECTED_PYTHON = "3.12"
_PHASE_RE = re.compile(r"^PHASE:(\w+)\s*$")
_EXC_RE = re.compile(r"^([A-Za-z_][\w.]*(?:Error|Exception|Exit|Interrupt))\b")


def _to_text(stream) -> str:
    """TimeoutExpired.stdout/stderr are bytes even with text=True."""
    if stream is None:
        return ""
    if isinstance(stream, bytes):
        return stream.decode("utf-8", errors="replace")
    return stream


def last_phase(stderr: str, default: str = "prepare") -> str:
    """Returns the last phase marker written by the worker."""
    phase = default
    for line in stderr.splitlines():
        m = _PHASE_RE.match(line.strip())
        if m:
            phase = m.group(1)
    return phase


def last_exception_name(stderr: str) -> Optional[str]:
    """Returns the exception class name from the last traceback line, if any."""
    for line in reversed(stderr.splitlines()):
        m = _EXC_RE.match(line.strip())
        if m:
            return m.group(1).rsplit(".", 1)[-1]
    return None


def build_cmd(cfg: dict[str, Any], code_commit: str) -> list[str]:
    cmd = [
        sys.executable, "-m", "bench.worker",
        "--run-id", str(cfg.get("run_id", "run_main")),
        "--rq", str(cfg.get("rq", "")),
        "--algo", str(cfg["algo"]),
        "--dataset", str(cfg["dataset"]),
        "--n", str(cfg["n"]),
        "--seed", str(cfg["seed"]),
        "--mode", str(cfg["mode"]),
        "--code-commit", code_commit,
        "--json",
    ]
    if cfg.get("k") is not None:
        cmd += ["--k", str(cfg["k"])]
    if cfg.get("runs") is not None:
        cmd += ["--runs", str(cfg["runs"])]
    return cmd


def error_record(
    cfg: dict[str, Any], code_commit: str, machine_id: str,
    status: str, error_type: str, phase: str,
) -> dict[str, Any]:
    """Standardised record for a trial that produced no result row."""
    rec = {col: "" for col in CSV_COLUMNS}
    try:
        algo = canonical_algorithm(str(cfg["algo"]))
    except ValueError:
        algo = str(cfg["algo"])
    rec.update({
        "run_id": cfg.get("run_id", "run_main"),
        "rq": cfg.get("rq", ""),
        "algorithm": algo,
        "code_commit": code_commit,
        "generator_version": GENERATOR_VERSION,
        "machine_id": machine_id,
        "python_version": platform.python_version(),
        "dataset": str(cfg["dataset"]).upper(),
        "n": cfg["n"],
        "k": cfg.get("k") if cfg.get("k") is not None else "",
        "runs": cfg.get("runs") if cfg.get("runs") is not None else "",
        "seed": cfg["seed"],
        "mode": cfg["mode"],
        "status": status,
        "phase": phase,
        "error_type": error_type,
        "oracle_match": False,
    })
    return rec


def run_single_trial(
    cfg: dict[str, Any], code_commit: str, machine_id: str, timeout: float = 60.0,
) -> dict[str, Any]:
    """Runs one trial in an isolated subprocess and returns its CSV record."""
    cmd = build_cmd(cfg, code_commit)
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        phase = last_phase(_to_text(exc.stderr))
        # The whole process exceeded the limit. phase tells where it was:
        # 'prepare' means the algorithm never started; do not report it as
        # "the algorithm needs more than 60 s".
        return error_record(cfg, code_commit, machine_id, "timeout", "TimeoutExpired", phase)
    except Exception as exc:  # could not even start the worker
        return error_record(cfg, code_commit, machine_id, "crash", type(exc).__name__, "prepare")

    stderr = proc.stderr or ""
    if proc.returncode == 0 and proc.stdout.strip():
        try:
            rec = json.loads(proc.stdout.strip().splitlines()[-1])
            return {col: rec.get(col, "") for col in CSV_COLUMNS}
        except (json.JSONDecodeError, IndexError):
            return error_record(cfg, code_commit, machine_id, "crash",
                                "WorkerOutputError", last_phase(stderr))

    # Abnormal exit: uncaught exception or killed by a signal.
    phase = last_phase(stderr)
    exc_name = last_exception_name(stderr)
    if exc_name == "MemoryError":
        return error_record(cfg, code_commit, machine_id, "oom", "MemoryError", phase)
    if exc_name:
        return error_record(cfg, code_commit, machine_id, "crash", exc_name, phase)
    if proc.returncode < 0:
        # Killed by a signal (e.g. 9 from the OS OOM killer). The plan forbids
        # guessing oom, so this stays crash with the signal number recorded.
        return error_record(cfg, code_commit, machine_id, "crash", f"Signal{-proc.returncode}", phase)
    return error_record(cfg, code_commit, machine_id, "crash", f"ExitCode{proc.returncode}", phase)


# ---------------------------------------------------------------- filtering

def _csv_list(value: Optional[str]) -> Optional[set[str]]:
    if not value:
        return None
    return {v.strip().lower() for v in value.split(",") if v.strip()}


def filter_configs(configs: list[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    rqs = _csv_list(args.rq)
    algos = _csv_list(args.algo)
    datasets = _csv_list(args.dataset)
    ns = _csv_list(args.n)
    modes = _csv_list(args.mode)
    seeds = _csv_list(args.seed)

    out = []
    for c in configs:
        if rqs and not ({r.lower() for r in str(c.get("rq", "")).split("+")} & rqs):
            continue
        if algos and str(c["algo"]).lower() not in algos:
            continue
        if datasets and str(c["dataset"]).lower() not in datasets:
            continue
        if ns and str(c["n"]) not in ns:
            continue
        if modes and str(c["mode"]).lower() not in modes:
            continue
        if seeds and str(c["seed"]) not in seeds:
            continue
        out.append(c)
    return out


def trial_key(algo, dataset, n, k, runs, seed, mode) -> tuple:
    def s(v):
        return "" if v is None else str(v)
    return (str(algo).lower(), str(dataset).upper(), s(n), s(k), s(runs), s(seed), str(mode))


def done_keys(csv_path: str, code_commit: str, machine_id: str) -> set[tuple]:
    """Trials already recorded in csv_path for this commit and machine."""
    if not os.path.exists(csv_path):
        return set()
    keys = set()
    with open(csv_path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("code_commit") != code_commit or row.get("machine_id") != machine_id:
                continue
            keys.add(trial_key(row["algorithm"], row["dataset"], row["n"], row["k"],
                               row["runs"], row["seed"], row["mode"]))
    return keys


# ---------------------------------------------------------------- execution

def check_python(strict: bool) -> None:
    current = platform.python_version()
    if current.startswith(EXPECTED_PYTHON + "."):
        return
    msg = (f"Python {current} is running, but the group agreed on CPython {EXPECTED_PYTHON}.x "
           f"for official measurements. Results from different versions must not be mixed.")
    if strict:
        sys.exit(f"ERROR: {msg}")
    print(f"WARNING: {msg}", file=sys.stderr)


def execute_matrix(
    configs: list[dict[str, Any]],
    output_csv_path: str,
    timeout: float = 60.0,
    resume: bool = False,
) -> None:
    """Runs configs sequentially and appends rows to output_csv_path."""
    code_commit = get_git_commit()
    machine_id = get_machine_id()
    if code_commit.endswith("-dirty") or code_commit == "workspace":
        print(f"WARNING: code_commit = '{code_commit}'. Commit your code before official runs "
              f"so every row can be traced to a commit.", file=sys.stderr)

    if resume:
        done = done_keys(output_csv_path, code_commit, machine_id)
        before = len(configs)
        configs = [c for c in configs
                   if trial_key(c["algo"], c["dataset"], c["n"], c.get("k"), c.get("runs"),
                                c["seed"], c["mode"]) not in done]
        print(f"Resume: {before - len(configs)} trials already in {output_csv_path}, "
              f"{len(configs)} left.")

    out_dir = os.path.dirname(os.path.abspath(output_csv_path))
    os.makedirs(out_dir, exist_ok=True)
    write_header = not os.path.exists(output_csv_path) or os.path.getsize(output_csv_path) == 0

    counts: dict[str, int] = {}
    total = len(configs)
    started = time.time()
    with open(output_csv_path, mode="a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        if write_header:
            writer.writeheader()
            f.flush()

        for idx, cfg in enumerate(configs, 1):
            extra = ""
            if cfg.get("k") is not None:
                extra = f" K={cfg['k']}"
            if cfg.get("runs") is not None:
                extra = f" R={cfg['runs']}"
            print(f"[{idx}/{total}] {cfg['algo']:<11} {cfg['dataset']}{extra:<7} "
                  f"n={cfg['n']:<8} seed={cfg['seed']} {cfg['mode']:<5} ... ", end="", flush=True)

            rec = run_single_trial(cfg, code_commit, machine_id, timeout=timeout)
            writer.writerow(rec)
            f.flush()
            counts[rec["status"]] = counts.get(rec["status"], 0) + 1

            detail = ""
            if rec["elapsed_ms"]:
                detail = f"{float(rec['elapsed_ms']):.1f} ms"
            elif rec["mem_peak_bytes"]:
                detail = f"{int(rec['mem_peak_bytes']) / 1024:.1f} KB"
            elif rec["key_comparisons"] or rec["array_reads"]:
                detail = f"cmp={rec['key_comparisons'] or '-'} reads={rec['array_reads'] or '-'}"
            if rec["status"] != "ok":
                detail = f"{rec['error_type']} (phase={rec['phase']})"
            print(f"{rec['status']} {detail}")

    mins = (time.time() - started) / 60
    summary = ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))
    print(f"Done: {total} trials in {mins:.1f} min. {summary}")


def pilot_configs() -> list[dict[str, Any]]:
    """Small smoke test: Heap, Radix and lib-sorted on D1, N=10k, one seed."""
    cfgs = []
    for algo in ("heap", "radix", "lib-sorted"):
        for mode in ("time", "mem", "count"):
            if algo == "lib-sorted" and mode == "count":
                continue
            cfgs.append({"run_id": "run_pilot", "rq": "pilot", "algo": algo, "dataset": "D1",
                         "n": 10000, "seed": 2026, "mode": mode})
    return cfgs


def main() -> None:
    parser = argparse.ArgumentParser(description="CSD203 Sorting Benchmark Runner")
    parser.add_argument("--config", type=str, help="JSON matrix (see bench/make_configs.py)")
    parser.add_argument("--out", type=str, default="results/raw/output.csv", help="Output CSV path")
    parser.add_argument("--timeout", type=float, default=60.0, help="Per-trial timeout in seconds")
    parser.add_argument("--pilot", action="store_true", help="Run a quick smoke test")
    parser.add_argument("--resume", action="store_true",
                        help="Skip trials already in --out for this commit and machine")
    parser.add_argument("--strict-python", action="store_true",
                        help=f"Abort unless running CPython {EXPECTED_PYTHON}.x")
    parser.add_argument("--dry-run", action="store_true", help="Only print how many trials would run")
    parser.add_argument("--rq", help="e.g. RQ2 or RQ1,RQ3")
    parser.add_argument("--algo", help="e.g. heap,radix")
    parser.add_argument("--dataset", help="e.g. D1,D3")
    parser.add_argument("--n", help="e.g. 100000")
    parser.add_argument("--mode", help="time, mem, count")
    parser.add_argument("--seed", help="e.g. 2026")
    args = parser.parse_args()

    if args.pilot:
        configs = pilot_configs()
    elif args.config:
        with open(args.config, "r", encoding="utf-8") as f:
            configs = json.load(f)
    else:
        parser.print_help()
        return

    configs = filter_configs(configs, args)
    if args.dry_run:
        print(f"{len(configs)} trials selected.")
        return

    check_python(args.strict_python)
    execute_matrix(configs, args.out, timeout=args.timeout, resume=args.resume)


if __name__ == "__main__":
    main()
