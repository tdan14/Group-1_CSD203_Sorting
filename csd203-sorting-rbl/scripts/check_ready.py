"""Exit 1 khi còn TODO; flag không thay thế test và review."""
from src.registry import ALGORITHMS, is_ready

def main():
    missing = []
    for name in ALGORITHMS:
        for mode in ("time", "mem", "count"):
            if name == "lib-sorted" and mode == "count":
                continue
            ready = is_ready(name, mode)
            print(f"{'READY' if ready else 'TODO ':5} {name}/{mode}")
            if not ready:
                missing.append((name, mode))
    print("Flags chỉ xác nhận bàn giao; phải chạy toàn bộ tests và review cơ chế.")
    return 1 if missing else 0
if __name__ == "__main__":
    raise SystemExit(main())
