"""Chạy từ repo root: python -m bench.runner --help."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import uuid
from bench.plan import official_plan
from bench.schema import FIELDS
from data.generate import GENERATOR_VERSION
from src.registry import ALGORITHMS, is_ready
ROOT = Path(__file__).resolve().parents[1]

def git_info():
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True))
        return commit, dirty
    except (OSError, subprocess.CalledProcessError):
        return "uncommitted", True

def execute(case, timeout=60):
    command = [sys.executable, "-m", "bench.worker", "--case", json.dumps(case)]
    try:
        cp = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        phases = [line[6:] for line in cp.stderr.splitlines() if line.startswith("PHASE=")]
        if cp.returncode:
            return dict(case, status="crash", phase=phases[-1] if phases else "startup", error_type=f"ProcessExit:{cp.returncode}")
        try:
            return json.loads(cp.stdout)
        except (ValueError, TypeError):
            return dict(case, status="crash", phase=phases[-1] if phases else "startup", error_type="InvalidWorkerJSON")
    except subprocess.TimeoutExpired as exc:
        stderr = exc.stderr or ""
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        phases = [line[6:] for line in stderr.splitlines() if line.startswith("PHASE=")]
        return dict(case, status="timeout", phase=phases[-1] if phases else "startup", error_type="TimeoutExpired")

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--official", action="store_true", help="Toàn ma trận, cần đủ module + môi trường + Git sạch")
    p.add_argument("--rq", nargs="+", choices=["RQ1", "RQ2", "RQ3"])
    p.add_argument("--algorithm", choices=ALGORITHMS, default="lib-sorted")
    p.add_argument("--dataset", choices=[f"D{i}" for i in range(1, 7)], default="D1")
    p.add_argument("--n", type=int, default=1000)
    p.add_argument("--seed", type=int, default=2026)
    p.add_argument("--k", type=int)
    p.add_argument("--runs", type=int)
    group = p.add_mutually_exclusive_group()
    group.add_argument("--mode", choices=["time", "mem", "count"], default="time")
    group.add_argument("--mem", dest="mode", action="store_const", const="mem")
    group.add_argument("--count", dest="mode", action="store_const", const="count")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--out", type=Path)
    args = p.parse_args(argv)
    cases = official_plan(args.rq) if args.official else [dict(algorithm=args.algorithm, dataset=args.dataset, n=args.n, seed=args.seed, mode=args.mode, k=args.k, runs=args.runs, rq="smoke")]
    if args.rq and not args.official:
        p.error("--rq dùng cùng --official")
    if args.dry_run:
        print(json.dumps({"worker_runs": len(cases), "cases": cases}, indent=2))
        return 0
    missing = sorted({c["algorithm"] + "/" + c["mode"] for c in cases if not is_ready(c["algorithm"], c["mode"])})
    if missing:
        p.error("Chưa triển khai: " + ", ".join(missing) + ". Không sinh kết quả giả; xem scripts.check_ready.")
    commit, dirty = git_info()
    env = json.loads((ROOT / "environment.json").read_text(encoding="utf-8"))
    if args.official:
        if platform.python_implementation() != "CPython" or sys.version_info[:2] != (3, 12):
            p.error("Benchmark chính thức cần CPython 3.12")
        if not env.get("captured") or env.get("python_version") != platform.python_version() or env.get("hostname") != platform.node():
            p.error("Chạy python -m scripts.capture_environment --machine-id hai-main trên máy đo rồi commit")
        if not env.get("ram_bytes") or env.get("cpu") in (None, "record-manually") or env.get("power_mode") in (None, "not-recorded"):
            p.error("Điền CPU, ram_bytes và power_mode thực tế vào environment.json rồi commit")
        if dirty:
            p.error("Commit toàn bộ thay đổi trước benchmark chính thức để gắn số liệu với source cụ thể")
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    folder = args.out or ROOT / "results" / ("raw" if args.official else "smoke") / run_id
    if folder.exists() and any(folder.iterdir()):
        p.error("Thư mục đầu ra không rỗng; chọn đường dẫn mới để giữ CSV gốc")
    folder.mkdir(parents=True, exist_ok=True)
    cfg = ROOT / "bench" / "configs.json"
    meta = dict(run_id=run_id, official=args.official, code_commit=commit, dirty=dirty, machine_id=env.get("machine_id") if env.get("captured") else "uncaptured-smoke", python_version=platform.python_version(), config_sha256=hashlib.sha256(cfg.read_bytes()).hexdigest(), cases=cases, environment=env)
    (folder / "manifest.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    with (folder / "measurements.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        for i, case in enumerate(cases, 1):
            result = execute(case)
            result.setdefault("generator_version", GENERATOR_VERSION)
            result.update({k:meta[k] for k in ("run_id", "code_commit", "machine_id", "python_version", "official")})
            writer.writerow(result)
            stream.flush()
            print(f"[{i}/{len(cases)}] {case['algorithm']}/{case['mode']}: {result['status']}")
    print(folder / "measurements.csv")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
