"""Generator tham chiếu D1-D6. My/Ngân sở hữu, kiểm tra và ghi log khi chỉnh."""
import hashlib
import random
import struct
GENERATOR_VERSION = "1.0.0"
MAX_VALUE = 2**31 - 1

def generate(dataset, n, seed, k=None, runs=None):
    if dataset not in {"D1", "D2", "D3", "D4", "D5", "D6"}:
        raise ValueError("dataset phải là D1..D6")
    if not isinstance(n, int) or isinstance(n, bool) or n < 0:
        raise ValueError("n phải là số nguyên không âm")
    if dataset != "D5" and k is not None:
        raise ValueError("k chỉ dùng với D5")
    if dataset != "D6" and runs is not None:
        raise ValueError("runs chỉ dùng với D6")
    rng = random.Random(seed)
    if dataset == "D5":
        if not isinstance(k, int) or isinstance(k, bool) or not 1 <= k <= MAX_VALUE + 1:
            raise ValueError("D5 cần k nguyên dương trong miền giá trị")
        keys = rng.sample(range(MAX_VALUE + 1), k)
        return [rng.choice(keys) for _ in range(n)]
    if dataset == "D6" and (not isinstance(runs, int) or isinstance(runs, bool) or runs < 1):
        raise ValueError("D6 cần runs nguyên dương")
    a = [rng.randint(0, MAX_VALUE) for _ in range(n)]
    if dataset == "D1":
        return a
    if dataset == "D6":
        q, r = divmod(n, runs)
        out, start = [], 0
        for i in range(runs):
            stop = start + q + (i < r)
            out.extend(sorted(a[start:stop]))
            start = stop
        return out
    a = sorted(a)
    if dataset == "D4":
        a.reverse()
    elif dataset == "D3":
        swaps = random.Random(seed + 10000)
        for _ in range(n // 1000):
            i, j = swaps.sample(range(n), 2)
            a[i], a[j] = a[j], a[i]
    return a

def input_sha256(a):
    digest = hashlib.sha256()
    for x in a:
        digest.update(struct.pack("<I", x))
    return digest.hexdigest()

def output_check(a):
    h = 0
    for x in a:
        h = (31 * h + x) % 2**64
    return str(h)
