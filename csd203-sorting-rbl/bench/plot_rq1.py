"""Script to analyze and visualize RQ1 benchmark results from standardized CSV.

CSD203 RBL Sorting Research Project.
Author: My (RQ1 Time & Throughput Lead)

Complies with the 27-column CSV schema specified in project proposal.
Does not import from src/ or run live sorting benchmarks.
"""

import argparse
import collections
import csv
import os
import statistics
import sys
from typing import Any, Dict, List, Optional, Tuple

EXPECTED_COLUMNS = [
    "run_id",
    "rq",
    "algorithm",
    "code_commit",
    "generator_version",
    "machine_id",
    "python_version",
    "dataset",
    "n",
    "k",
    "runs",
    "seed",
    "input_sha256",
    "mode",
    "status",
    "phase",
    "error_type",
    "output_check",
    "oracle_match",
    "elapsed_ms",
    "throughput_kps",
    "mem_peak_bytes",
    "key_comparisons",
    "array_reads",
    "array_writes",
    "run_count",
    "avg_run_len",
]


def parse_and_validate_csv(csv_path: str) -> List[Dict[str, str]]:
    """Read CSV file and validate that header contains required columns."""
    if not os.path.isfile(csv_path):
        print(f"Error: File not found: {csv_path}", file=sys.stderr)
        sys.exit(1)

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            print("Error: Empty or corrupted CSV file.", file=sys.stderr)
            sys.exit(1)

        # Check column presence
        missing_cols = [c for c in EXPECTED_COLUMNS if c not in reader.fieldnames]
        if missing_cols:
            print(
                f"Error: CSV missing required columns: {missing_cols}",
                file=sys.stderr,
            )
            sys.exit(1)

        return list(reader)


def aggregate_rq1_data(
    rows: List[Dict[str, str]]
) -> Tuple[
    Dict[Tuple[str, int], Dict[str, Any]],
    List[Dict[str, str]],
    str,
    str,
]:
    """Aggregate benchmark results for RQ1.

    Enforces environment isolation and filters for status == 'ok'.
    """
    # 1. Environment isolation: Group by (machine_id, code_commit)
    env_counts: Dict[Tuple[str, str], int] = collections.defaultdict(int)
    for r in rows:
        if r.get("status") == "ok":
            env_key = (r.get("machine_id", "unknown"), r.get("code_commit", "unknown"))
            env_counts[env_key] += 1

    if not env_counts:
        print("Warning: No records with status == 'ok' found.")
        target_machine, target_commit = "unknown", "unknown"
    else:
        target_machine, target_commit = max(env_counts, key=lambda k: env_counts[k])
        if len(env_counts) > 1:
            print(
                f"Warning: Multiple environments detected. Isolating to most frequent "
                f"environment: machine_id='{target_machine}', commit='{target_commit}'"
            )

    # 2. Filter rows for isolated environment
    valid_groups: Dict[Tuple[str, int], List[Dict[str, float]]] = collections.defaultdict(list)
    discarded_rows: List[Dict[str, str]] = []

    for r in rows:
        # Verify environment match
        if (
            r.get("machine_id", "unknown") != target_machine
            or r.get("code_commit", "unknown") != target_commit
        ):
            continue

        algo = r.get("algorithm", "").strip()
        try:
            n = int(r.get("n", 0))
        except ValueError:
            n = 0

        status = r.get("status", "").strip().lower()
        oracle = str(r.get("oracle_match", "")).strip().lower() in ("true", "1", "ok")

        if status == "ok" and oracle:
            try:
                elapsed_ms = float(r.get("elapsed_ms", 0.0))
            except ValueError:
                elapsed_ms = 0.0

            # Calculate throughput if omitted
            raw_tput = r.get("throughput_kps", "").strip()
            if raw_tput:
                try:
                    throughput_kps = float(raw_tput)
                except ValueError:
                    throughput_kps = n / elapsed_ms if elapsed_ms > 0 else 0.0
            else:
                throughput_kps = n / elapsed_ms if elapsed_ms > 0 else 0.0

            valid_groups[(algo, n)].append(
                {"elapsed_ms": elapsed_ms, "throughput_kps": throughput_kps}
            )
        else:
            discarded_rows.append(r)

    # 3. Calculate summary metrics (median, min, max, ok_count)
    summary: Dict[Tuple[str, int], Dict[str, Any]] = {}
    for (algo, n), records in valid_groups.items():
        elapsed_vals = [rec["elapsed_ms"] for rec in records]
        tput_vals = [rec["throughput_kps"] for rec in records]

        summary[(algo, n)] = {
            "ok_count": len(records),
            "elapsed_median": statistics.median(elapsed_vals) if elapsed_vals else 0.0,
            "elapsed_min": min(elapsed_vals) if elapsed_vals else 0.0,
            "elapsed_max": max(elapsed_vals) if elapsed_vals else 0.0,
            "tput_median": statistics.median(tput_vals) if tput_vals else 0.0,
            "tput_min": min(tput_vals) if tput_vals else 0.0,
            "tput_max": max(tput_vals) if tput_vals else 0.0,
        }

    return summary, discarded_rows, target_machine, target_commit


def print_summary_table(
    summary: Dict[Tuple[str, int], Dict[str, Any]],
    discarded_rows: List[Dict[str, str]],
    machine_id: str,
    code_commit: str,
) -> None:
    """Print structured summary table to stdout."""
    print("=" * 88)
    print(f" RQ1 BENCHMARK SUMMARY (Machine: {machine_id} | Commit: {code_commit})")
    print("=" * 88)
    print(
        f"{'Algorithm':<14} | {'N':<10} | {'Status':<8} | "
        f"{'Elapsed (ms) Med [Min - Max]':<30} | {'Throughput (kps) Median':<20}"
    )
    print("-" * 88)

    # Sort algorithms and N values
    all_algos = sorted({k[0] for k in summary.keys()})
    all_ns = sorted({k[1] for k in summary.keys()})

    for algo in all_algos:
        for n in all_ns:
            if (algo, n) in summary:
                s = summary[(algo, n)]
                elapsed_str = (
                    f"{s['elapsed_median']:8.2f} [{s['elapsed_min']:8.2f} - {s['elapsed_max']:8.2f}]"
                )
                status_str = f"{s['ok_count']}/3 ok"
                tput_str = f"{s['tput_median']:12.2f}"
                print(
                    f"{algo:<14} | {n:<10,d} | {status_str:<8} | {elapsed_str:<30} | {tput_str:<20}"
                )
        print("-" * 88)

    if discarded_rows:
        print("\nDiscarded / Incomplete Runs:")
        for dr in discarded_rows:
            print(
                f" - Algo: {dr.get('algorithm')}, N: {dr.get('n')}, Seed: {dr.get('seed')}, "
                f"Status: {dr.get('status')}, Phase: {dr.get('phase')}, Error: {dr.get('error_type')}"
            )
        print("=" * 88)


def plot_rq1_figures(
    summary: Dict[Tuple[str, int], Dict[str, Any]],
    outdir: str,
) -> None:
    """Generate IEEE-standardized publication plots for RQ1 using matplotlib."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n[Notice] matplotlib is not installed. Skipping figure generation.")
        print("To generate figures, run: pip install -r requirements-plot.txt")
        return

    os.makedirs(outdir, exist_ok=True)

    algos = sorted({k[0] for k in summary.keys()})
    ns = sorted({k[1] for k in summary.keys()})

    # Styling colors and markers
    color_map = {
        "quick": "#1f77b4",  # Blue
        "merge": "#ff7f0e",  # Orange
        "heap": "#2ca02c",  # Green
        "radix": "#d62728",  # Red
        "lib-sorted": "#7f7f7f",  # Gray baseline
    }
    marker_map = {
        "quick": "o",
        "merge": "s",
        "heap": "^",
        "radix": "D",
        "lib-sorted": "x",
    }

    # =========================================================================
    # Figure 1: Elapsed Time vs N (Log-Log Scale)
    # =========================================================================
    plt.figure(figsize=(6.5, 4.5), dpi=300)
    for algo in algos:
        x_vals: List[int] = []
        y_medians: List[float] = []
        y_err_lower: List[float] = []
        y_err_upper: List[float] = []

        for n in ns:
            if (algo, n) in summary:
                s = summary[(algo, n)]
                med = s["elapsed_median"]
                x_vals.append(n)
                y_medians.append(med)
                y_err_lower.append(med - s["elapsed_min"])
                y_err_upper.append(s["elapsed_max"] - med)

        if not x_vals:
            continue

        c = color_map.get(algo, "#333333")
        m = marker_map.get(algo, "o")
        ls = "--" if algo == "lib-sorted" else "-"
        lbl = f"{algo} (baseline)" if algo == "lib-sorted" else algo

        plt.errorbar(
            x_vals,
            y_medians,
            yerr=[y_err_lower, y_err_upper],
            label=lbl,
            color=c,
            marker=m,
            linestyle=ls,
            capsize=3,
            linewidth=1.5,
        )

    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Input Size N (elements)", fontsize=10)
    plt.ylabel("Execution Time (ms) [Log Scale]", fontsize=10)
    plt.title("RQ1: Execution Time Scaling on Uniform Random Data (D1)", fontsize=11, fontweight="bold")
    plt.grid(True, which="both", linestyle=":", alpha=0.6)
    plt.legend(fontsize=9, loc="upper left")
    plt.tight_layout()

    fig1_path = os.path.join(outdir, "rq1_elapsed_vs_n.png")
    plt.savefig(fig1_path)
    plt.close()
    print(f"Saved Figure 1 to: {fig1_path}")

    # =========================================================================
    # Figure 2: Throughput (kilo-elements/sec) Grouped Bar Chart
    # =========================================================================
    plt.figure(figsize=(6.8, 4.5), dpi=300)
    import numpy as np

    x_indices = np.arange(len(ns))
    num_algos = len(algos)
    bar_width = 0.8 / max(1, num_algos)

    for i, algo in enumerate(algos):
        tput_medians: List[float] = []
        tput_errs: List[float] = []
        for n in ns:
            if (algo, n) in summary:
                s = summary[(algo, n)]
                med = s["tput_median"]
                tput_medians.append(med)
                err = max(med - s["tput_min"], s["tput_max"] - med)
                tput_errs.append(err)
            else:
                tput_medians.append(0.0)
                tput_errs.append(0.0)

        offset = (i - num_algos / 2.0 + 0.5) * bar_width
        c = color_map.get(algo, "#333333")
        lbl = f"{algo} (baseline)" if algo == "lib-sorted" else algo

        plt.bar(
            x_indices + offset,
            tput_medians,
            width=bar_width,
            yerr=tput_errs,
            label=lbl,
            color=c,
            capsize=2,
            edgecolor="black",
            linewidth=0.5,
        )

    plt.xticks(x_indices, [f"{n:,}" for n in ns], fontsize=9)
    plt.xlabel("Input Size N (elements)", fontsize=10)
    plt.ylabel("Throughput (kilo-elements / second)", fontsize=10)
    plt.title("RQ1: Throughput Comparison Across Scaling Sizes", fontsize=11, fontweight="bold")
    plt.grid(True, axis="y", linestyle=":", alpha=0.6)
    plt.legend(fontsize=9, loc="upper right")
    plt.tight_layout()

    fig2_path = os.path.join(outdir, "rq1_throughput_kps.png")
    plt.savefig(fig2_path)
    plt.close()
    print(f"Saved Figure 2 to: {fig2_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze and plot RQ1 sorting benchmark results."
    )
    parser.add_argument(
        "csv_path",
        nargs="?",
        default="results/raw/rq1_benchmark.csv",
        help="Path to benchmark CSV (defaults to results/raw/rq1_benchmark.csv)",
    )
    parser.add_argument(
        "--outdir",
        default="results/figures",
        help="Output directory for generated figures (defaults to results/figures)",
    )
    args = parser.parse_args()

    rows = parse_and_validate_csv(args.csv_path)
    summary, discarded, machine_id, commit_id = aggregate_rq1_data(rows)
    print_summary_table(summary, discarded, machine_id, commit_id)
    plot_rq1_figures(summary, args.outdir)


if __name__ == "__main__":
    main()
