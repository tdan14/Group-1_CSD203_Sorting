import json
from pathlib import Path
CONFIG = Path(__file__).with_name("configs.json")

def official_plan(rqs=None):
    cases = json.loads(CONFIG.read_text(encoding="utf-8"))
    if rqs is None:
        return cases
    selected = []
    for case in cases:
        for rq in case["rq"].split("+"):
            if rq in rqs:
                selected.append(case)
                break
    return selected
