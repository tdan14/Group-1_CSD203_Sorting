"""Builds the experiment matrix for RQ1, RQ2 and RQ3 (bench/configs.json).

Module: bench/make_configs.py
Author: Hai (rq2-hai)
Project: CSD203 Sorting RBL

Group plan:
- RQ1: quick, merge, heap, radix | D1 | N = 10k, 50k, 100k, 500k, 1M
- RQ2: quick, merge, heap, radix | 10 dataset configs | N = 100k, 1M
- RQ3: quick, merge, timsort, timsort-noA, lib-sorted | 10 dataset configs | N = 100k, 1M
- Seeds 2026, 2027, 2028; modes time, mem, count (lib-sorted: time, mem only).

Identical trials needed by several RQs are merged and run once
("Hai gop cac cau hinh trung nhau"). The `rq` field lists every RQ that uses
the trial, e.g. "RQ1+RQ2+RQ3". The runner's --rq filter matches any of them.

Usage:
    python -m bench.make_configs                      # writes bench/configs.json
    python -m bench.make_configs --out other.json --run-id run_2026_10_30
"""

import argparse
import json
from collections import OrderedDict

SEEDS = (2026, 2027, 2028)
MODES = ("time", "mem", "count")

BASIC_ALGOS = ("quick", "merge", "heap", "radix")
RQ3_ALGOS = ("quick", "merge", "timsort", "timsort-noA", "lib-sorted")

RQ1_SIZES = (10_000, 50_000, 100_000, 500_000, 1_000_000)
RQ23_SIZES = (100_000, 1_000_000)

# The 10 dataset configurations of RQ2/RQ3: (dataset, k, runs)
DATASET_CONFIGS = (
    ("D1", None, None),
    ("D2", None, None),
    ("D3", None, None),
    ("D4", None, None),
    ("D5", 1000, None),
    ("D5", 10, None),
    ("D5", 2, None),
    ("D6", None, 2),
    ("D6", None, 16),
    ("D6", None, 256),
)


def modes_for(algo: str) -> tuple[str, ...]:
    return ("time", "mem") if algo == "lib-sorted" else MODES


def build_matrix(run_id: str, rqs: tuple[str, ...] = ("RQ1", "RQ2", "RQ3")) -> list[dict]:
    """Returns the deduplicated list of trial configurations."""
    trials: "OrderedDict[tuple, dict]" = OrderedDict()

    def add(rq: str, algo: str, dataset: str, n: int, k, runs) -> None:
        for seed in SEEDS:
            for mode in modes_for(algo):
                key = (algo, dataset, n, k, runs, seed, mode)
                if key in trials:
                    if rq not in trials[key]["_rqs"]:
                        trials[key]["_rqs"].append(rq)
                    continue
                cfg = {"run_id": run_id, "_rqs": [rq], "algo": algo, "dataset": dataset,
                       "n": n, "seed": seed, "mode": mode}
                if k is not None:
                    cfg["k"] = k
                if runs is not None:
                    cfg["runs"] = runs
                trials[key] = cfg

    if "RQ1" in rqs:
        for algo in BASIC_ALGOS:
            for n in RQ1_SIZES:
                add("RQ1", algo, "D1", n, None, None)
    if "RQ2" in rqs:
        for algo in BASIC_ALGOS:
            for n in RQ23_SIZES:
                for ds, k, runs in DATASET_CONFIGS:
                    add("RQ2", algo, ds, n, k, runs)
    if "RQ3" in rqs:
        for algo in RQ3_ALGOS:
            for n in RQ23_SIZES:
                for ds, k, runs in DATASET_CONFIGS:
                    add("RQ3", algo, ds, n, k, runs)

    result = []
    for cfg in trials.values():
        rq_list = cfg.pop("_rqs")
        out = {"run_id": cfg["run_id"], "rq": "+".join(sorted(rq_list))}
        out.update({k: v for k, v in cfg.items() if k != "run_id"})
        result.append(out)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Build deduplicated experiment matrix")
    parser.add_argument("--out", default="bench/configs.json")
    parser.add_argument("--run-id", default="run_main")
    parser.add_argument("--rq", nargs="+", default=["RQ1", "RQ2", "RQ3"])
    args = parser.parse_args()

    matrix = build_matrix(args.run_id, tuple(args.rq))
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(matrix, f, indent=1)

    per_rq = {rq: sum(1 for c in matrix if rq in c["rq"].split("+")) for rq in args.rq}
    print(f"Wrote {len(matrix)} unique trials to {args.out}")
    for rq, cnt in per_rq.items():
        print(f"  {rq}: {cnt} trials")
    print(f"  merged (shared by >1 RQ): {sum(1 for c in matrix if '+' in c['rq'])}")


if __name__ == "__main__":
    main()
