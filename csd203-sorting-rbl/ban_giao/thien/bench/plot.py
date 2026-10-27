"""Benchmark Plotting Script for CSD203 Sorting RBL.

Module: bench/plot.py
Authors: Hai, Thien (rq2-thien)
Project: CSD203 Sorting RBL

Generates comparative charts from benchmark CSV results for RQ1, RQ2, and RQ3.
Strictly separated from performance measurement to avoid overhead.
"""

import argparse
import csv
import os
from collections import defaultdict
from typing import Any

import matplotlib.pyplot as plt


def load_csv_data(csv_path: str) -> list[dict[str, Any]]:
    """Loads benchmark CSV records."""
    records = []
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("status") == "ok":
                records.append(row)
    return records


def aggregate_by_metric(
    records: list[dict[str, Any]],
    metric_col: str,
    group_keys: list[str],
) -> dict[tuple, list[float]]:
    """Groups metric values across seeds to allow computing median/min/max."""
    groups = defaultdict(list)
    for r in records:
        val_str = r.get(metric_col, "")
        if val_str != "" and val_str is not None:
            try:
                val = float(val_str)
                key = tuple(r.get(k, "") for k in group_keys)
                groups[key].append(val)
            except ValueError:
                continue
    return groups


def plot_rq2_throughput_comparison(
    records: list[dict[str, Any]],
    n_target: int,
    output_dir: str = "results/figures",
) -> str:
    """Plots throughput (kps) comparison across datasets D1-D6 for algorithms at size N."""
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"rq2_throughput_N{n_target}.png")

    # Filter for target N and RQ2
    filtered = [
        r for r in records
        if r.get("mode") == "time" and str(r.get("n")) == str(n_target)
    ]

    if not filtered:
        print(f"No time records found for N={n_target} to plot RQ2 throughput.")
        return ""

    # Group by (dataset_label, algorithm)
    def make_dataset_label(r):
        ds = r.get("dataset", "")
        if ds == "D5":
            return f"D5 (K={r.get('k', '')})"
        if ds == "D6":
            return f"D6 (R={r.get('runs', '')})"
        return ds

    dataset_order = [
        "D1", "D2", "D3", "D4",
        "D5 (K=1000)", "D5 (K=10)", "D5 (K=2)",
        "D6 (R=2)", "D6 (R=16)", "D6 (R=256)",
    ]

    algos = sorted(list(set(r.get("algorithm") for r in filtered)))
    data_by_algo_ds = defaultdict(dict)

    for r in filtered:
        ds_lbl = make_dataset_label(r)
        algo = r.get("algorithm")
        tp_str = r.get("throughput_kps", "")
        if tp_str:
            try:
                tp = float(tp_str)
                if algo not in data_by_algo_ds[ds_lbl]:
                    data_by_algo_ds[ds_lbl][algo] = []
                data_by_algo_ds[ds_lbl][algo].append(tp)
            except ValueError:
                pass

    active_datasets = [d for d in dataset_order if d in data_by_algo_ds]
    if not active_datasets:
        active_datasets = sorted(list(data_by_algo_ds.keys()))

    plt.figure(figsize=(12, 6))
    x_indices = list(range(len(active_datasets)))
    bar_width = 0.8 / max(1, len(algos))

    for idx, algo in enumerate(algos):
        medians = []
        for ds in active_datasets:
            vals = data_by_algo_ds[ds].get(algo, [])
            if vals:
                vals.sort()
                med = vals[len(vals) // 2]
                medians.append(med)
            else:
                medians.append(0)

        offsets = [x + idx * bar_width - 0.4 + bar_width / 2 for x in x_indices]
        plt.bar(offsets, medians, width=bar_width, label=algo.upper(), alpha=0.9)

    plt.title(f"RQ2: Throughput Comparison Across Datasets (N = {n_target:,})", fontsize=14, fontweight="bold")
    plt.xlabel("Dataset Configuration", fontsize=12)
    plt.ylabel("Throughput (k elements / sec)", fontsize=12)
    plt.xticks(x_indices, active_datasets, rotation=30, ha="right")
    plt.legend(title="Algorithm")
    plt.grid(axis="y", linestyle="--", alpha=0.6)
    plt.tight_layout()

    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved figure: {out_path}")
    return out_path


def plot_rq2_memory_comparison(
    records: list[dict[str, Any]],
    n_target: int,
    output_dir: str = "results/figures",
) -> str:
    """Plots peak memory usage (mem_peak_bytes) across algorithms for N."""
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"rq2_memory_N{n_target}.png")

    filtered = [
        r for r in records
        if r.get("mode") == "mem" and str(r.get("n")) == str(n_target)
    ]

    if not filtered:
        return ""

    algo_mem = defaultdict(list)
    for r in filtered:
        m_str = r.get("mem_peak_bytes", "")
        if m_str:
            try:
                algo_mem[r.get("algorithm")].append(float(m_str) / 1024.0)  # Convert to KB
            except ValueError:
                pass

    algos = sorted(list(algo_mem.keys()))
    medians = []
    for a in algos:
        vals = algo_mem[a]
        vals.sort()
        medians.append(vals[len(vals) // 2] if vals else 0)

    plt.figure(figsize=(8, 5))
    bars = plt.bar(algos, medians, color=["#2b5c8f", "#d95f02", "#7570b3", "#e7298a"][:len(algos)])
    plt.title(f"Peak Memory Allocation (N = {n_target:,})", fontsize=13, fontweight="bold")
    plt.xlabel("Algorithm", fontsize=11)
    plt.ylabel("Peak Memory (KB)", fontsize=11)
    plt.grid(axis="y", linestyle="--", alpha=0.6)

    for bar, val in zip(bars, medians):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5, f"{val:.1f} KB", ha="center", va="bottom", fontsize=10)

    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved figure: {out_path}")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="CSD203 Sorting Benchmark Plotter")
    parser.add_argument("--csv", type=str, required=True, help="Path to input CSV")
    parser.add_argument("--out-dir", type=str, default="results/figures", help="Output figures directory")
    parser.add_argument("--n", type=int, default=10000, help="N to filter and plot")

    args = parser.parse_args()
    records = load_csv_data(args.csv)
    print(f"Loaded {len(records)} valid records from {args.csv}")

    plot_rq2_throughput_comparison(records, args.n, args.out_dir)
    plot_rq2_memory_comparison(records, args.n, args.out_dir)


if __name__ == "__main__":
    main()
