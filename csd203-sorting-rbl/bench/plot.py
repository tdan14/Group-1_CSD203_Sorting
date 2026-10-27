"""Benchmark Plotting Script for CSD203 Sorting RBL.

Module: bench/plot.py
Authors: Hai, Thien (rq2-thien)
Project: CSD203 Sorting RBL

Reads the raw benchmark CSV and produces, for one RQ at a time:
- figures (PNG 300 dpi + PDF for the IEEE paper) and
- a summary CSV with median / min / max / n_ok per group, so every number in
  a figure can be traced back to the raw CSV (group plan, acceptance rules).

Rules enforced (group plan, "Tong hop"):
- Only status == ok rows are used for values; failed rows are counted and
  shown (e.g. "2/3" above a bar, "n/a" where nothing succeeded).
- Median / min / max over the three seeds; error bars span min..max.
- Rows from different machines, commits, Python versions or generator
  versions are never mixed: the script stops and asks for --machine/--commit.
- Radix reports array reads/writes, not key comparisons, so it is plotted in
  the "array accesses" panel only, never next to comparison counts.

Usage:
    python -m bench.plot --csv results/raw/main.csv --rq RQ1
    python -m bench.plot --csv results/raw/main.csv --rq RQ2            # both N
    python -m bench.plot --csv results/raw/main.csv --rq RQ3 --n 100000
Matplotlib is used only here, outside the measurement code.
"""

import argparse
import csv
import math
import os
import statistics
import sys
from collections import Counter, defaultdict
from typing import Any, Optional

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FuncFormatter, LogLocator  # noqa: E402

# ------------------------------------------------------------------ style
# Colour follows the algorithm, never its position, so the same algorithm has
# the same colour in every figure. Orders were checked with a colour-vision-
# deficiency validator for the bar orders used below (RQ1/RQ2: quick, merge,
# heap, radix; RQ3: quick, merge, timsort, timsort-noA, lib-sorted).
COLORS = {
    "quick": "#2a78d6",        # blue
    "merge": "#eb6834",        # orange
    "heap": "#1baf7a",         # aqua
    "radix": "#eda100",        # yellow
    "timsort": "#6250d6",      # violet
    "timsort-noA": "#e87ba4",  # magenta
    "lib-sorted": "#008300",   # green
}
# Hatch + marker = second encoding for grayscale print and colour-blind readers.
HATCHES = {
    "quick": "", "merge": "//", "heap": "..", "radix": "\\\\",
    "timsort": "", "timsort-noA": "xx", "lib-sorted": "--",
}
MARKERS = {
    "quick": "o", "merge": "s", "heap": "^", "radix": "D",
    "timsort": "v", "timsort-noA": "P", "lib-sorted": "X",
}
ALGO_ORDER = ["quick", "merge", "heap", "radix", "timsort", "timsort-noA", "lib-sorted"]

SURFACE = "#ffffff"
TEXT = "#0b0b0b"
TEXT2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
POS = "#2a78d6"   # diverging pole: improvement
NEG = "#e34948"   # diverging pole: regression

DATASET_ORDER = [
    ("D1", "", ""), ("D2", "", ""), ("D3", "", ""), ("D4", "", ""),
    ("D5", "1000", ""), ("D5", "10", ""), ("D5", "2", ""),
    ("D6", "", "2"), ("D6", "", "16"), ("D6", "", "256"),
]

RQ_ALGOS = {
    "RQ1": ["quick", "merge", "heap", "radix"],
    "RQ2": ["quick", "merge", "heap", "radix"],
    "RQ3": ["quick", "merge", "timsort", "timsort-noA", "lib-sorted"],
}

IDENTITY_FIELDS = ("machine_id", "code_commit", "python_version", "generator_version")


def apply_style() -> None:
    plt.rcParams.update({
        "font.size": 8,
        "axes.titlesize": 9,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.labelsize": 8,
        "axes.labelcolor": TEXT2,
        "axes.edgecolor": MUTED,
        "axes.linewidth": 0.6,
        "axes.facecolor": SURFACE,
        "figure.facecolor": SURFACE,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "xtick.color": TEXT2,
        "ytick.color": TEXT2,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "legend.fontsize": 7,
        "legend.frameon": False,
        "text.color": TEXT,
        "hatch.color": SURFACE,
        "hatch.linewidth": 0.8,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
    })


def dataset_label(ds: str, k: str, runs: str) -> str:
    if ds == "D5":
        return f"D5 K={k}"
    if ds == "D6":
        return f"D6 R={runs}"
    return ds


# ------------------------------------------------------------------ loading

def load_rows(csv_path: str) -> list[dict[str, str]]:
    with open(csv_path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def select_rows(rows: list[dict[str, str]], rq: str, machine: Optional[str],
                commit: Optional[str]) -> list[dict[str, str]]:
    """Rows belonging to `rq` from a single, consistent environment."""
    sel = [r for r in rows if rq in r.get("rq", "").split("+")]
    if machine:
        sel = [r for r in sel if r.get("machine_id") == machine]
    if commit:
        sel = [r for r in sel if r.get("code_commit") == commit]
    if not sel:
        sys.exit(f"No rows for {rq} (after --machine/--commit filters).")

    problems = []
    for field in IDENTITY_FIELDS:
        values = sorted({r.get(field, "") for r in sel})
        if len(values) > 1:
            problems.append(f"  {field}: {values}")
    if problems:
        sys.exit(
            "Rows come from more than one environment; the group plan forbids mixing them.\n"
            + "\n".join(problems)
            + "\nRe-run with --machine and/or --commit to pick one, "
              "or remove the other rows from the CSV."
        )
    return sel


class Group:
    """All trials of one (algorithm, dataset config, n, mode)."""

    def __init__(self) -> None:
        self.rows: list[dict[str, str]] = []

    def ok_values(self, metric: str) -> list[float]:
        vals = []
        for r in self.rows:
            if r.get("status") != "ok":
                continue
            v = r.get(metric, "")
            if v not in ("", None):
                vals.append(float(v))
        return vals

    def n_total(self) -> int:
        return len(self.rows)

    def failures(self) -> str:
        c = Counter(r.get("status") for r in self.rows if r.get("status") != "ok")
        return ";".join(f"{k}={v}" for k, v in sorted(c.items()))


def group_rows(rows: list[dict[str, str]]) -> dict[tuple, Group]:
    groups: dict[tuple, Group] = defaultdict(Group)
    for r in rows:
        key = (r["algorithm"], r["dataset"], r.get("k", ""), r.get("runs", ""), r["n"], r["mode"])
        groups[key].rows.append(r)
    return groups


def stats_of(vals: list[float]) -> Optional[tuple[float, float, float]]:
    if not vals:
        return None
    return statistics.median(vals), min(vals), max(vals)


# ------------------------------------------------------------------ summary CSV

SUMMARY_FIELDS = ["rq", "algorithm", "dataset", "k", "runs", "n", "mode", "metric",
                  "n_ok", "n_total", "failures", "median", "min", "max",
                  "machine_id", "code_commit", "python_version", "generator_version"]

METRICS_BY_MODE = {
    "time": ["elapsed_ms", "throughput_kps"],
    "mem": ["mem_peak_bytes"],
    "count": ["key_comparisons", "array_reads", "array_writes", "run_count", "avg_run_len"],
}


def write_summary(path: str, rq: str, groups: dict[tuple, Group], env: dict[str, str]) -> None:
    lines = []
    for key in sorted(groups, key=lambda k: (ALGO_ORDER.index(k[0]) if k[0] in ALGO_ORDER else 99,
                                             int(k[4]), k[1], k[2], k[3], k[5])):
        algo, ds, k, runs, n, mode = key
        g = groups[key]
        for metric in METRICS_BY_MODE.get(mode, []):
            vals = g.ok_values(metric)
            if not vals and g.failures() == "":
                continue  # metric not applicable (e.g. key_comparisons for radix)
            st = stats_of(vals)
            lines.append({
                "rq": rq, "algorithm": algo, "dataset": ds, "k": k, "runs": runs, "n": n,
                "mode": mode, "metric": metric, "n_ok": len(vals), "n_total": g.n_total(),
                "failures": g.failures(),
                "median": "" if st is None else f"{st[0]:.6g}",
                "min": "" if st is None else f"{st[1]:.6g}",
                "max": "" if st is None else f"{st[2]:.6g}",
                **env,
            })
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SUMMARY_FIELDS)
        w.writeheader()
        w.writerows(lines)
    print(f"Saved summary: {path}")


# ------------------------------------------------------------------ helpers

def time_unit(max_ms: float) -> tuple[float, str]:
    return (1000.0, "s") if max_ms >= 2000 else (1.0, "ms")


def mem_unit(max_bytes: float) -> tuple[float, str]:
    if max_bytes >= 1024 ** 2:
        return 1024.0 ** 2, "MiB"
    if max_bytes >= 1024:
        return 1024.0, "KiB"
    return 1.0, "B"


def fmt_bytes(b: float) -> str:
    for unit, div in (("MiB", 1024 ** 2), ("KiB", 1024)):
        if b >= div:
            return f"{b / div:.3g} {unit}"
    return f"{b:.0f} B"


def count_unit(max_val: float) -> tuple[float, str]:
    if max_val >= 1e6:
        return 1e6, "millions"
    if max_val >= 1e3:
        return 1e3, "thousands"
    return 1.0, ""


def finish(fig, out_base: str) -> None:
    fig.savefig(out_base + ".png")
    fig.savefig(out_base + ".pdf")
    plt.close(fig)
    print(f"Saved figure: {out_base}.png / .pdf")


def footer(fig, env: dict[str, str]) -> None:
    fig.text(0.0, -0.02,
             f"Bars/points: median of 3 seeds; whiskers: min-max. "
             f"machine={env['machine_id']}, Python {env['python_version']}, "
             f"commit {env['code_commit']}, generator {env['generator_version']}.",
             fontsize=6, color=MUTED, ha="left", va="top")


# ------------------------------------------------------------------ grouped bars (RQ2 / RQ3)

def grouped_bars(ax, groups: dict[tuple, Group], algos: list[str], n: str, mode: str,
                 metric: str, scale: float, ylabel: str, log: bool = False,
                 tiny_fmt=None) -> bool:
    """Draws one grouped bar chart (x = dataset config, bars = algorithms).

    tiny_fmt: optional function(raw_value) -> str. Bars under 2 % of the axis
    height get their value written above them, so a near-zero bar (e.g. the
    in-place Heap Sort in the memory chart) is not mistaken for missing data.
    """
    ds_list = [d for d in DATASET_ORDER
               if any((a, d[0], d[1], d[2], n, mode) in groups for a in algos)]
    algos = [a for a in algos if any((a, d[0], d[1], d[2], n, mode) in groups for d in ds_list)
             and any(groups[(a, d[0], d[1], d[2], n, mode)].ok_values(metric)
                     or groups[(a, d[0], d[1], d[2], n, mode)].failures()
                     for d in ds_list if (a, d[0], d[1], d[2], n, mode) in groups)]
    if not ds_list or not algos:
        return False

    width = 0.8 / len(algos)
    top = 0.0
    labels_to_place = []
    tiny = []  # (xpos, median_scaled, raw_median)
    for i, algo in enumerate(algos):
        xs, meds, lo, hi = [], [], [], []
        for x, (ds, k, runs) in enumerate(ds_list):
            g = groups.get((algo, ds, k, runs, n, mode))
            xpos = x - 0.4 + width * (i + 0.5)
            if g is None:
                continue
            vals = g.ok_values(metric)
            st = stats_of(vals)
            if st is None:
                if g.failures():
                    labels_to_place.append((xpos, None, "n/a"))
                continue
            med, mn, mx = (v / scale for v in st)
            xs.append(xpos)
            meds.append(med)
            lo.append(med - mn)
            hi.append(mx - med)
            top = max(top, mx)
            tiny.append((xpos, med, st[0]))
            if len(vals) < g.n_total():
                labels_to_place.append((xpos, mx, f"{len(vals)}/{g.n_total()}"))
        if xs:
            ax.bar(xs, meds, width=width, color=COLORS.get(algo, MUTED), hatch=HATCHES.get(algo, ""),
                   edgecolor=SURFACE, linewidth=0.8, label=algo, zorder=2)
            ax.errorbar(xs, meds, yerr=[lo, hi], fmt="none", ecolor=TEXT2,
                        elinewidth=0.6, capsize=1.2, zorder=3)

    if tiny_fmt is not None and not log and top > 0:
        for xpos, med, raw in tiny:
            if med < 0.02 * top:
                ax.text(xpos, med + 0.01 * top, tiny_fmt(raw), rotation=90, ha="center",
                        va="bottom", fontsize=5.5, color=TEXT2)

    for xpos, y, text in labels_to_place:
        if y is None:
            ax.text(xpos, 0, text, rotation=90, ha="center", va="bottom", fontsize=5.5, color=MUTED)
        else:
            ax.text(xpos, y, text, ha="center", va="bottom", fontsize=5.5, color=TEXT2)

    ax.set_xticks(range(len(ds_list)))
    ax.set_xticklabels([dataset_label(*d) for d in ds_list], rotation=0)
    ax.set_xlim(-0.55, len(ds_list) - 0.45)
    ax.set_ylabel(ylabel)
    if log:
        ax.set_yscale("log")
    else:
        ax.set_ylim(0, top * 1.12 if top > 0 else 1)
    ax.grid(axis="y", color=GRID, linewidth=0.5, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", length=0)
    return True


def legend_top(fig, ax) -> None:
    """Legend in its own row between the title and the plot area."""
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        ax.legend(handles, labels, loc="lower left", bbox_to_anchor=(0.0, 1.0), ncol=len(labels),
                  handlelength=1.4, columnspacing=1.2, borderaxespad=0.2)
        ax.set_title(ax.get_title(loc="left"), loc="left", pad=18)


def max_metric(groups, algos, n, mode, metric) -> float:
    m = 0.0
    for key, g in groups.items():
        if key[0] in algos and key[4] == n and key[5] == mode:
            vals = g.ok_values(metric)
            if vals:
                m = max(m, max(vals))
    return m


def plot_by_dataset(rq: str, groups, n: str, out_dir: str, env, log: bool) -> None:
    algos = RQ_ALGOS[rq]
    tag = f"{rq.lower()}_N{n}"
    n_txt = f"{int(n):,}"

    # Time
    scale, unit = time_unit(max_metric(groups, algos, n, "time", "elapsed_ms"))
    fig, ax = plt.subplots(figsize=(7.16, 2.6))
    if grouped_bars(ax, groups, algos, n, "time", "elapsed_ms", scale,
                    f"Sort time ({unit}, lower is better)", log):
        ax.set_title(f"{rq}: sort time by dataset, N = {n_txt}")
        legend_top(fig, ax)
        footer(fig, env)
        finish(fig, os.path.join(out_dir, f"{tag}_time"))
    else:
        plt.close(fig)

    # Memory
    scale, unit = mem_unit(max_metric(groups, algos, n, "mem", "mem_peak_bytes"))
    fig, ax = plt.subplots(figsize=(7.16, 2.6))
    if grouped_bars(ax, groups, algos, n, "mem", "mem_peak_bytes", scale,
                    f"Peak extra memory ({unit})", False, tiny_fmt=fmt_bytes):
        ax.set_title(f"{rq}: peak extra memory (tracemalloc) by dataset, N = {n_txt}")
        legend_top(fig, ax)
        footer(fig, env)
        finish(fig, os.path.join(out_dir, f"{tag}_memory"))
    else:
        plt.close(fig)

    # Operation counts: (a) key comparisons, (b) array reads + writes
    cmp_algos = [a for a in algos if max_metric(groups, [a], n, "count", "key_comparisons") > 0]
    acc_algos = [a for a in algos if max_metric(groups, [a], n, "count", "array_reads") > 0]
    if cmp_algos or acc_algos:
        fig, axes = plt.subplots(2, 1, figsize=(7.16, 4.6), sharex=False)
        drawn = False
        if cmp_algos:
            s, u = count_unit(max_metric(groups, cmp_algos, n, "count", "key_comparisons"))
            drawn |= grouped_bars(axes[0], groups, cmp_algos, n, "count", "key_comparisons", s,
                                  f"Key comparisons ({u})", log)
            axes[0].set_title(f"(a) {rq}: key comparisons, N = {n_txt}")
        else:
            axes[0].set_visible(False)
        if acc_algos:
            s, u = count_unit(max_metric(groups, acc_algos, n, "count", "array_reads"))
            drawn |= grouped_bars(axes[1], groups, acc_algos, n, "count", "array_reads", s,
                                  f"Array reads ({u})", log)
            axes[1].set_title("(b) array reads - a different unit from (a); "
                              "Radix is non-comparative and appears only here")
        else:
            axes[1].set_visible(False)
        if drawn:
            # one legend covering every algorithm drawn in either panel
            seen = {}
            for ax in axes:
                for h, l in zip(*ax.get_legend_handles_labels()):
                    seen.setdefault(l, h)
            fig.legend(list(seen.values()), list(seen.keys()), loc="upper right",
                       ncol=len(seen), bbox_to_anchor=(1.0, 1.01))
            fig.tight_layout(h_pad=1.6)
            footer(fig, env)
            finish(fig, os.path.join(out_dir, f"{tag}_ops"))
        else:
            plt.close(fig)


# ------------------------------------------------------------------ RQ3 ablation

def plot_ablation(groups, n: str, out_dir: str, env) -> list[dict[str, Any]]:
    """Reduction from natural-run detection: (T_noA - T_timsort) / T_noA * 100 %."""
    rows = []
    for ds, k, runs in DATASET_ORDER:
        g_t = groups.get(("timsort", ds, k, runs, n, "time"))
        g_a = groups.get(("timsort-noA", ds, k, runs, n, "time"))
        if g_t is None or g_a is None:
            continue
        st_t = stats_of(g_t.ok_values("elapsed_ms"))
        st_a = stats_of(g_a.ok_values("elapsed_ms"))
        row = {"dataset": ds, "k": k, "runs": runs, "n": n,
               "n_ok_timsort": len(g_t.ok_values("elapsed_ms")), "n_ok_noA": len(g_a.ok_values("elapsed_ms")),
               "median_ms_timsort": "", "median_ms_noA": "", "reduction_pct": ""}
        if st_t and st_a:
            red = (st_a[0] - st_t[0]) / st_a[0] * 100.0
            row.update(median_ms_timsort=f"{st_t[0]:.4f}", median_ms_noA=f"{st_a[0]:.4f}",
                       reduction_pct=f"{red:.2f}")
        rows.append(row)

    usable = [r for r in rows if r["reduction_pct"] != ""]
    if not usable:
        return rows

    fig, ax = plt.subplots(figsize=(7.16, 2.4))
    xs = list(range(len(rows)))
    for x, r in zip(xs, rows):
        if r["reduction_pct"] == "":
            ax.text(x, 0, "n/a", ha="center", va="bottom", fontsize=6, color=MUTED)
            continue
        v = float(r["reduction_pct"])
        ax.bar(x, v, width=0.6, color=POS if v >= 0 else NEG, edgecolor=SURFACE, linewidth=0.8, zorder=2)
        ax.text(x, v, f"{v:+.1f}%", ha="center", va="bottom" if v >= 0 else "top",
                fontsize=6, color=TEXT2)
        if r["n_ok_timsort"] < 3 or r["n_ok_noA"] < 3:
            ax.text(x, 0, f"{r['n_ok_timsort']}/{r['n_ok_noA']} ok", ha="center", va="top",
                    fontsize=5.5, color=MUTED)
    ax.axhline(0, color=TEXT2, linewidth=0.6, zorder=3)
    ax.set_xticks(xs)
    ax.set_xticklabels([dataset_label(r["dataset"], r["k"], r["runs"]) for r in rows])
    ax.tick_params(axis="x", length=0)
    ax.set_ylabel("Time reduction vs noA (%)\n(> 0: timsort faster)")
    ax.grid(axis="y", color=GRID, linewidth=0.5, zorder=0)
    ax.set_axisbelow(True)
    lo = min(0.0, min(float(r["reduction_pct"]) for r in usable))
    hi = max(0.0, max(float(r["reduction_pct"]) for r in usable))
    pad = (hi - lo) * 0.15 or 5
    ax.set_ylim(lo - pad, hi + pad)
    ax.set_title(f"RQ3 ablation: natural-run detection, N = {int(n):,}")
    fig.text(0.0, -0.02,
             "Reduction = (T_noA - T_timsort) / T_noA x 100 %, using medians of 3 seeds. "
             "Negative values are valid results. "
             f"machine={env['machine_id']}, Python {env['python_version']}, commit {env['code_commit']}.",
             fontsize=6, color=MUTED, ha="left", va="top")
    finish(fig, os.path.join(out_dir, f"rq3_N{n}_ablation"))
    return rows


def write_rq3_tables(groups, n: str, out_dir: str, ablation_rows: list[dict[str, Any]]) -> None:
    """Speedup table: baseline time / timsort time (group plan definition)."""
    path = os.path.join(out_dir, f"rq3_N{n}_speedup.csv")
    fields = ["dataset", "k", "runs", "n", "baseline", "median_ms_baseline",
              "median_ms_timsort", "speedup_baseline_over_timsort"]
    out = []
    for ds, k, runs in DATASET_ORDER:
        t = stats_of(groups.get(("timsort", ds, k, runs, n, "time"), Group()).ok_values("elapsed_ms"))
        for base in ("quick", "merge", "timsort-noA", "lib-sorted"):
            b = stats_of(groups.get((base, ds, k, runs, n, "time"), Group()).ok_values("elapsed_ms"))
            if t is None and b is None:
                continue
            out.append({
                "dataset": ds, "k": k, "runs": runs, "n": n, "baseline": base,
                "median_ms_baseline": "" if b is None else f"{b[0]:.4f}",
                "median_ms_timsort": "" if t is None else f"{t[0]:.4f}",
                "speedup_baseline_over_timsort": "" if (b is None or t is None) else f"{b[0] / t[0]:.3f}",
            })
    if out:
        with open(path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(out)
        print(f"Saved table: {path}")
    if ablation_rows:
        path = os.path.join(out_dir, f"rq3_N{n}_ablation.csv")
        with open(path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(ablation_rows[0].keys()))
            w.writeheader()
            w.writerows(ablation_rows)
        print(f"Saved table: {path}")


# ------------------------------------------------------------------ RQ1 scaling lines

def scaling_panel(ax, groups, algos, mode, metric, ylabel, unit_fn) -> bool:
    sizes = sorted({int(k[4]) for k in groups if k[1] == "D1" and k[5] == mode})
    if not sizes:
        return False
    maxv = max((max(g.ok_values(metric)) for k, g in groups.items()
                if k[0] in algos and k[1] == "D1" and k[5] == mode and g.ok_values(metric)), default=0)
    if maxv <= 0:
        return False
    scale, unit = unit_fn(maxv)
    drawn = False
    ends = []  # (algo, x_last, y_last) for direct labels
    all_y: list[float] = []
    for algo in algos:
        xs, meds, lo, hi = [], [], [], []
        for n in sizes:
            g = groups.get((algo, "D1", "", "", str(n), mode))
            if g is None:
                continue
            st = stats_of(g.ok_values(metric))
            if st is None:
                continue
            med, mn, mx = (v / scale for v in st)
            xs.append(n)
            meds.append(med)
            lo.append(med - mn)
            hi.append(mx - med)
        if not xs:
            continue
        drawn = True
        ax.errorbar(xs, meds, yerr=[lo, hi], color=COLORS[algo], marker=MARKERS[algo],
                    markersize=4, linewidth=1.4, elinewidth=0.6, capsize=1.5,
                    markeredgecolor=SURFACE, markeredgewidth=0.6, label=algo, zorder=3)
        ends.append((algo, xs[-1], meds[-1]))
        all_y.extend(v for v in (m - l for m, l in zip(meds, lo)) if v > 0)
        all_y.extend(m + h for m, h in zip(meds, hi))
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xticks(sizes)
    ax.set_xticklabels([f"{s // 1000}k" if s < 1_000_000 else f"{s / 1e6:g}M" for s in sizes])
    ax.minorticks_off()
    decades = math.log10(max(all_y) / min(all_y)) if all_y and min(all_y) > 0 else 0
    # 1-2-5 ticks only when the data spans few decades; otherwise powers of 10
    subs = (1.0, 2.0, 5.0) if decades <= 2.5 else (1.0,)
    ax.yaxis.set_major_locator(LogLocator(base=10, subs=subs))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    ax.set_xlabel("N (log)")
    ax.set_ylabel(f"{ylabel} ({unit + ', ' if unit else ''}log)")
    ax.grid(color=GRID, linewidth=0.5, zorder=0)
    ax.set_axisbelow(True)
    ax.margins(x=0.12)
    ax._end_labels = ends  # placed by the caller after the final layout
    return drawn


def place_end_labels(ax, ends: list[tuple[str, float, float]], min_gap_pt: float = 7.5) -> None:
    """Direct labels at line ends, pushed apart vertically so they never overlap."""
    if not ends:
        return
    fig = ax.figure
    fig.canvas.draw()  # finalise limits so data->display transform is correct
    px_per_pt = fig.dpi / 72.0
    items = []
    for algo, x, y in ends:
        _, y_disp = ax.transData.transform((x, y))
        items.append([algo, x, y, y_disp, y_disp])
    items.sort(key=lambda it: it[3])
    gap = min_gap_pt * px_per_pt
    for i in range(1, len(items)):  # push upwards
        if items[i][4] - items[i - 1][4] < gap:
            items[i][4] = items[i - 1][4] + gap
    for algo, x, y, y_disp, y_new in items:
        ax.annotate(algo, (x, y), xytext=(4, (y_new - y_disp) / px_per_pt),
                    textcoords="offset points", fontsize=6.5, color=TEXT2, va="center",
                    annotation_clip=False)


def plot_rq1(groups, out_dir: str, env) -> None:
    algos = RQ_ALGOS["RQ1"]
    fig, axes = plt.subplots(1, 3, figsize=(7.16, 2.5))
    ok1 = scaling_panel(axes[0], groups, algos, "time", "elapsed_ms", "Time", time_unit)
    axes[0].set_title("(a) Sort time")
    ok2 = scaling_panel(axes[1], groups, algos, "mem", "mem_peak_bytes", "Peak memory", mem_unit)
    axes[1].set_title("(b) Peak extra memory")
    cmp_algos = [a for a in algos if a != "radix"]
    ok3 = scaling_panel(axes[2], groups, cmp_algos, "count", "key_comparisons", "Key comparisons", count_unit)
    axes[2].set_title("(c) Key comparisons")
    if not (ok1 or ok2 or ok3):
        plt.close(fig)
        print("RQ1: nothing to plot.")
        return
    seen = {}
    for ax in axes:
        for h, l in zip(*ax.get_legend_handles_labels()):
            seen.setdefault(l, h)
    fig.legend(list(seen.values()), list(seen.keys()), loc="upper right", ncol=len(seen),
               bbox_to_anchor=(1.0, 1.06))
    fig.suptitle("RQ1: scaling on random data (D1)", x=0.0, ha="left", y=1.06,
                 fontsize=9, fontweight="bold")
    fig.tight_layout(w_pad=3.0)
    for ax in axes:
        place_end_labels(ax, getattr(ax, "_end_labels", []))
    fig.text(0.0, -0.03, "(c) excludes Radix Sort (non-comparative; its array reads/writes are in "
             "the summary CSV). " f"machine={env['machine_id']}, Python {env['python_version']}, "
             f"commit {env['code_commit']}.", fontsize=6, color=MUTED, ha="left", va="top")
    finish(fig, os.path.join(out_dir, "rq1_scaling"))


# ------------------------------------------------------------------ main

def main() -> None:
    parser = argparse.ArgumentParser(description="CSD203 Sorting Benchmark Plotter")
    parser.add_argument("--csv", required=True, help="Raw benchmark CSV from bench.runner")
    parser.add_argument("--rq", required=True, choices=["RQ1", "RQ2", "RQ3"])
    parser.add_argument("--n", type=int, nargs="*", default=None,
                        help="N levels for RQ2/RQ3 (default: 100000 1000000)")
    parser.add_argument("--out-dir", default="results/figures")
    parser.add_argument("--machine", help="Use only rows from this machine_id")
    parser.add_argument("--commit", help="Use only rows from this code_commit")
    parser.add_argument("--log", action="store_true", help="Log-scale y axis for time/ops bars")
    args = parser.parse_args()

    apply_style()
    os.makedirs(args.out_dir, exist_ok=True)

    rows = select_rows(load_rows(args.csv), args.rq, args.machine, args.commit)
    env = {f: rows[0].get(f, "") for f in IDENTITY_FIELDS}
    groups = group_rows(rows)
    n_ok = sum(1 for r in rows if r.get("status") == "ok")
    print(f"{args.rq}: {len(rows)} rows ({n_ok} ok, {len(rows) - n_ok} failed) "
          f"from machine={env['machine_id']} commit={env['code_commit']}")

    write_summary(os.path.join(args.out_dir, f"{args.rq.lower()}_summary.csv"), args.rq, groups, env)

    if args.rq == "RQ1":
        plot_rq1(groups, args.out_dir, env)
        return

    levels = [str(n) for n in (args.n or [100_000, 1_000_000])]
    for n in levels:
        if not any(k[4] == n for k in groups):
            print(f"{args.rq}: no rows for N={n}, skipped.")
            continue
        plot_by_dataset(args.rq, groups, n, args.out_dir, env, args.log)
        if args.rq == "RQ3":
            write_rq3_tables(groups, n, args.out_dir, plot_ablation(groups, n, args.out_dir, env))


if __name__ == "__main__":
    main()
