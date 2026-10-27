"""Vẽ timing theo N từ summary. Matplotlib chỉ import trong lệnh này."""
import argparse
import csv
from collections import defaultdict
from pathlib import Path
import re

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("summary",type=Path)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--include-incomplete",action="store_true",help="Chỉ dùng xem thử; biểu đồ gắn nhãn chưa đủ 3 seed")
    a=p.parse_args()
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        p.error("Cài pip install -r requirements-plot.txt")
    with a.summary.open(encoding="utf-8",newline="") as stream:
        rows=list(csv.DictReader(stream))
    groups=defaultdict(list)
    for row in rows:
        if row["mode"]!="time" or not row.get("elapsed_ms_median"):
            continue
        if not a.include_incomplete and row["complete"]!="True":
            continue
        key=tuple(row.get(k,"") for k in ("run_id","machine_id","code_commit","dataset","k","runs"))
        groups[key].append(row)
    if not groups:
        p.error("Không có timing đủ điều kiện; xem --include-incomplete cho smoke")
    a.out.mkdir(parents=True,exist_ok=True)
    for index,(key,samples) in enumerate(groups.items(),1):
        fig,ax=plt.subplots(figsize=(7,4.5),layout="constrained")
        for algorithm in sorted({r["algorithm"] for r in samples}):
            selected=sorted((r for r in samples if r["algorithm"]==algorithm),key=lambda r:int(r["n"]))
            xs=[int(r["n"]) for r in selected];ys=[float(r["elapsed_ms_median"]) for r in selected]
            lo=[y-float(r["elapsed_ms_min"]) for r,y in zip(selected,ys)]
            hi=[float(r["elapsed_ms_max"])-y for r,y in zip(selected,ys)]
            ax.errorbar(xs,ys,yerr=[lo,hi],marker="o",label=algorithm)
        ax.set(xlabel="N (elements)",ylabel="Elapsed time (ms)",title=f"{key[3]} | K={key[4] or '-'} R={key[5] or '-'}" + (" | preview / incomplete allowed" if a.include_incomplete else " | median, min-max, 3 seeds"))
        ax.legend();ax.grid(alpha=.2)
        stem=re.sub(r"[^A-Za-z0-9_.-]","_",f"{index:02d}_{key[0]}_{key[3]}_K{key[4]}_R{key[5]}")
        for ext in ("png","svg"):
            target=a.out/(stem+"."+ext)
            if target.exists():
                p.error(f"Không ghi đè {target}")
            fig.savefig(target,dpi=180)
        plt.close(fig)
    print(f"{len(groups)} charts in {a.out}")
if __name__=="__main__":
    main()
