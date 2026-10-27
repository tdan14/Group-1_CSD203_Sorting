import json
from pathlib import Path
CONFIG = Path(__file__).with_name("configs.json")

def official_plan(rqs=None):
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    selected = rqs or list(cfg["rqs"])
    merged = {}
    for rq in selected:
        group = cfg["rqs"][rq]
        for data in group.get("datasets", cfg["condition_datasets"]):
            for n in group["sizes"]:
                for algorithm in group["algorithms"]:
                    for seed in cfg["seeds"]:
                        for mode in cfg["modes"]:
                            if algorithm == "lib-sorted" and mode == "count":
                                continue
                            case = dict(data, n=n, algorithm=algorithm, seed=seed, mode=mode)
                            key = json.dumps(case, sort_keys=True)
                            if key not in merged:
                                merged[key] = dict(case, rq=rq)
                            elif rq not in merged[key]["rq"].split(";"):
                                merged[key]["rq"] += ";" + rq
    return list(merged.values())
