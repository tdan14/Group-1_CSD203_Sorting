"""Noi test va cong cu kiem tra voi giao dien ban giao cua cac thanh vien."""
from importlib import import_module

from bench.worker import ALGORITHMS, get_algorithm_callable

STABLE = ("merge", "timsort", "timsort-noA")


def is_ready(name, mode="time"):
    if name not in ALGORITHMS:
        raise ValueError(name)
    if name == "lib-sorted":
        return mode in ("time", "mem")
    if mode not in ("time", "mem", "count"):
        return False

    module_name = name
    if name == "timsort-noA":
        module_name = "timsort"
    try:
        module = import_module("src." + module_name)
        function = get_algorithm_callable(name, counted=(mode == "count"))
    except (ImportError, AttributeError):
        return False

    flag = "READY"
    if mode == "count":
        flag = "COUNTED_READY"
    if name == "timsort-noA":
        flag = "NOA_READY"
        if mode == "count":
            flag = "NOA_COUNTED_READY"
    return callable(function) and bool(getattr(module, flag, True))


def resolve(name, mode="time"):
    if not is_ready(name, mode):
        raise NotImplementedError(name + "/" + mode + ": chua ban giao")
    return get_algorithm_callable(name, counted=(mode == "count"))
