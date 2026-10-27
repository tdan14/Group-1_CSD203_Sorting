"""Chỉ tổng hợp CSV thật; không gộp khác run, máy, commit hoặc mode."""
import argparse
import csv
from collections import defaultdict
from pathlib import Path
import statistics
GROUP = ("run_id", "rq", "algorithm", "code_commit", "generator_version", "machine_id", "python_version", "dataset", "n", "k", "runs", "mode", "official")
METRICS = ("elapsed_ms", "throughput_kps", "mem_peak_bytes", "key_comparisons", "array_reads", "array_writes", "run_count", "avg_run_len")

def summarize(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[tuple(row.get(k, "") for k in GROUP)].append(row)
    output = []
    for key, samples in groups.items():
        result = dict(zip(GROUP, key))
        seeds = [r["seed"] for r in samples]
        if len(seeds) != len(set(seeds)):
            raise ValueError("Trùng seed trong một nhóm; không gộp hai lần đo như seed độc lập")
        good = [r for r in samples if r["status"] == "ok"]
        official = str(result["official"]).lower() == "true"
        result.update(total_count=len(samples), ok_count=len(good), failed_count=len(samples)-len(good), complete=official and len(good)==3 and {r["seed"] for r in good}=={"2026","2027","2028"})
        for metric in METRICS:
            values = [float(r[metric]) for r in good if r.get(metric) not in ("", None)]
            result[metric+"_count"] = len(values)
            for suffix, fn in (("median",statistics.median),("min",min),("max",max)):
                result[metric+"_"+suffix] = fn(values) if values else ""
        output.append(result)
    return output

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("csv", nargs="+", type=Path)
    p.add_argument("--out", type=Path, required=True)
    a=p.parse_args()
    if a.out.exists():
        p.error("File đầu ra đã tồn tại; chọn tên mới")
    rows=[]
    for file in a.csv:
        with file.open(encoding="utf-8",newline="") as stream:
            rows.extend(csv.DictReader(stream))
    output=summarize(rows)
    if not output:
        p.error("Không có dòng dữ liệu")
    a.out.parent.mkdir(parents=True,exist_ok=True)
    with a.out.open("w",encoding="utf-8",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(output[0]))
        writer.writeheader();writer.writerows(output)
    print(a.out)
if __name__=="__main__":
    main()
