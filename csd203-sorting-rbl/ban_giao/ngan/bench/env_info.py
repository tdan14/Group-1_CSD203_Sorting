"""Writes environment.json for the measurement machine.

Module: bench/env_info.py
Author: Hai (rq2-hai)
Project: CSD203 Sorting RBL

Group plan: "Hai ghi CPU, RAM, he dieu hanh, phien ban Python va che do nguon
vao environment.json ... Khong dien thong so phan cung khi chua kiem tra thuc te."
This script reads the values from the machine itself (Windows, Linux, macOS).
Power mode cannot be read reliably on every OS, so it must be filled by hand
with --power-mode after checking the OS settings (and the laptop must stay
plugged in during official runs).

Usage (run on the measurement machine, inside the venv used for benchmarking):
    python -m bench.env_info --role main --power-mode "Plugged in, Best performance"
"""

import argparse
import json
import os
import platform
import socket
import subprocess
import sys
from datetime import datetime, timezone
from typing import Optional


def _run(cmd: list[str]) -> str:
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return res.stdout.strip() if res.returncode == 0 else ""
    except Exception:
        return ""


def cpu_name() -> str:
    system = platform.system()
    if system == "Windows":
        out = _run(["powershell", "-NoProfile", "-Command",
                    "(Get-CimInstance Win32_Processor | Select-Object -First 1).Name"])
        return out or platform.processor()
    if system == "Linux":
        try:
            with open("/proc/cpuinfo", encoding="utf-8") as f:
                for line in f:
                    if line.lower().startswith("model name"):
                        return line.split(":", 1)[1].strip()
        except OSError:
            pass
    if system == "Darwin":
        out = _run(["sysctl", "-n", "machdep.cpu.brand_string"])
        if out:
            return out
    return platform.processor() or "unknown"


def ram_gb() -> Optional[float]:
    system = platform.system()
    try:
        if system == "Windows":
            import ctypes

            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("sullAvailExtendedVirtual", ctypes.c_ulonglong)]

            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
            return round(stat.ullTotalPhys / 1024 ** 3, 1)
        if system == "Linux":
            with open("/proc/meminfo", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        return round(int(line.split()[1]) / 1024 ** 2, 1)
        if system == "Darwin":
            out = _run(["sysctl", "-n", "hw.memsize"])
            if out:
                return round(int(out) / 1024 ** 3, 1)
    except Exception:
        pass
    return None


def os_name() -> str:
    system = platform.system()
    if system == "Linux":
        try:
            with open("/etc/os-release", encoding="utf-8") as f:
                info = dict(line.rstrip().split("=", 1) for line in f if "=" in line)
            pretty = info.get("PRETTY_NAME", "").strip('"')
            return f"{pretty} (kernel {platform.release()}, {platform.machine()})"
        except OSError:
            pass
    if system == "Windows":
        return f"Windows {platform.release()} (build {platform.version()}, {platform.machine()})"
    return f"{system} {platform.release()} ({platform.machine()})"


def main() -> None:
    parser = argparse.ArgumentParser(description="Record the measurement environment")
    parser.add_argument("--out", default="environment.json")
    parser.add_argument("--role", default="main", choices=["main", "backup", "dev"],
                        help="main = official measurement machine")
    parser.add_argument("--power-mode", default="",
                        help='Fill after checking the OS, e.g. "Plugged in, Best performance"')
    parser.add_argument("--note", default="")
    args = parser.parse_args()

    env = {
        "machine_id": socket.gethostname(),
        "role": args.role,
        "os": os_name(),
        "cpu": cpu_name(),
        "logical_cpus": os.cpu_count(),
        "ram_gb": ram_gb(),
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
        "python_executable": sys.executable,
        "power_mode": args.power_mode or "TODO: check OS power settings and fill in",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "note": args.note,
    }
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(env, f, indent=2, ensure_ascii=False)
    print(json.dumps(env, indent=2, ensure_ascii=False))
    if not platform.python_version().startswith("3.12."):
        print(f"WARNING: Python {platform.python_version()} - the group agreed on CPython 3.12.x.",
              file=sys.stderr)
    if not args.power_mode:
        print("WARNING: power_mode not filled. Re-run with --power-mode after checking.", file=sys.stderr)


if __name__ == "__main__":
    main()
