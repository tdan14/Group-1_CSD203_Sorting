import argparse
import json
import os
from pathlib import Path
import platform
import sys

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--machine-id", required=True)
    p.add_argument("--power-mode", default="not-recorded")
    p.add_argument("--out", type=Path, default=Path("environment.json"))
    a = p.parse_args()
    result = dict(captured=True, machine_id=a.machine_id, hostname=platform.node(), python_version=platform.python_version(), implementation=platform.python_implementation(), executable=sys.executable, os=platform.platform(), cpu=platform.processor() or "record-manually", logical_cpus=os.cpu_count(), ram_bytes=None, power_mode=a.power_mode)
    a.out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(f"Saved {a.out}; điền RAM/CPU/chế độ nguồn còn thiếu trước khi commit.")
if __name__ == "__main__":
    main()
