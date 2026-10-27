"""Một worker cho một thuật toán/dataset/seed/mode. Stdout chỉ chứa JSON."""
import argparse
import gc
import json
import sys
import time
import tracemalloc
from data.generate import generate, input_sha256, output_check, GENERATOR_VERSION
from src.registry import resolve
from src.contracts import METRIC_FIELDS

def run(case):
    result = dict(case, generator_version=GENERATOR_VERSION)
    phase = "setup"
    def mark(value):
        nonlocal phase
        phase = value
        print("PHASE=" + value, file=sys.stderr, flush=True)
    try:
        mark("generate")
        a = generate(case["dataset"], case["n"], case["seed"], case.get("k"), case.get("runs"))
        result["input_sha256"] = input_sha256(a)
        original = a.copy()
        algorithm, mode = case["algorithm"], case["mode"]
        fn = resolve(algorithm, mode)
        gc.enable()
        mark("warmup")
        warm = generate(case["dataset"], min(case["n"], 1000), case["seed"], case.get("k"), case.get("runs"))
        fn(warm)
        del warm
        mark("algorithm")
        if mode == "time":
            start = time.perf_counter_ns()
            returned = fn(a)
            elapsed = time.perf_counter_ns() - start
            result["elapsed_ms"] = elapsed / 1_000_000
            result["throughput_kps"] = case["n"] / result["elapsed_ms"] if elapsed > 0 else None
        elif mode == "mem":
            tracemalloc.start()
            returned = fn(a)
            result["mem_peak_bytes"] = tracemalloc.get_traced_memory()[1]
            tracemalloc.stop()
        elif mode == "count":
            returned = fn(a)
            if not isinstance(returned, dict) or set(returned) != set(METRIC_FIELDS):
                raise ValueError("sort_counted cần dict đúng METRIC_FIELDS")
            required = ("array_reads", "array_writes") if algorithm == "radix" else ("key_comparisons",)
            for field in required:
                if type(returned[field]) is not int or returned[field] < 0:
                    raise ValueError("Counter không hợp lệ: " + field)
            result.update(returned)
        else:
            raise ValueError("mode không hợp lệ")
        mark("validate")
        if algorithm == "lib-sorted":
            a = returned
        elif mode != "count" and returned is not None:
            raise ValueError("sort(a) phải trả None")
        result["output_check"] = output_check(a)
        result["oracle_match"] = a == sorted(original)
        result["status"] = "ok" if result["oracle_match"] else "wrong"
        if not result["oracle_match"]:
            for name in ("elapsed_ms", "throughput_kps", "mem_peak_bytes", *METRIC_FIELDS):
                result.pop(name, None)
        result["phase"] = "done"
    except Exception as exc:
        result.update(status="oom" if isinstance(exc, MemoryError) else "crash", phase=phase, error_type=type(exc).__name__ + ": " + str(exc)[:300])
        for name in ("elapsed_ms", "throughput_kps", "mem_peak_bytes", *METRIC_FIELDS):
            result.pop(name, None)
    finally:
        if tracemalloc.is_tracing():
            tracemalloc.stop()
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True)
    args = parser.parse_args()
    print(json.dumps(run(json.loads(args.case)), ensure_ascii=True, allow_nan=False))
