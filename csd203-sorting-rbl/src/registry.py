"""Điểm nối duy nhất giữa runner/test và module của từng thành viên."""
from importlib import import_module
ALGORITHMS = ("quick", "merge", "heap", "radix", "timsort", "timsort-noA", "lib-sorted")
STABLE = ("merge", "timsort", "timsort-noA")

def is_ready(name, mode="time"):
    if name == "lib-sorted":
        return mode in ("time", "mem")
    if name not in ALGORITHMS:
        raise ValueError(name)
    module = import_module("src." + ("timsort" if name == "timsort-noA" else name))
    flag = ("NOA_COUNTED_READY" if mode == "count" else "NOA_READY") if name == "timsort-noA" else ("COUNTED_READY" if mode == "count" else "READY")
    return bool(getattr(module, flag, False))

def resolve(name, mode="time"):
    if not is_ready(name, mode):
        raise NotImplementedError(f"{name}/{mode}: module chưa bàn giao; xem PHAN_CONG.md")
    if name == "lib-sorted":
        return sorted
    module = import_module("src." + ("timsort" if name == "timsort-noA" else name))
    fn = ("sort_noa_counted" if mode == "count" else "sort_noa") if name == "timsort-noA" else ("sort_counted" if mode == "count" else "sort")
    return getattr(module, fn)
