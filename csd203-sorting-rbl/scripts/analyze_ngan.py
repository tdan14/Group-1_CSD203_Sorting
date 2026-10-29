"""Audit the real experiment, then regenerate Ngan's tables and paper figures.

Run from the project root: python -B -m scripts.analyze_ngan
No measurement is synthesized. Source identity, trial coverage, data hashes,
oracle checksums, seed completeness and units are checked before publication.
"""
import argparse
import csv
import hashlib
import json
import math
import statistics
import struct
from collections import Counter, defaultdict
from pathlib import Path

from data.generate import generate, GENERATOR_VERSION

ROOT = Path(__file__).resolve().parents[1]
SEEDS = {"2026", "2027", "2028"}
BASIC = ("quick", "merge", "heap", "radix")
SIZES = (10000, 50000, 100000, 500000, 1000000)
FAMILIES = (("D1", "", ""), ("D2", "", ""), ("D3", "", ""),
            ("D4", "", ""), ("D5", "1000", ""), ("D5", "10", ""),
            ("D5", "2", ""), ("D6", "", "2"), ("D6", "", "16"),
            ("D6", "", "256"))
LABELS = ("D1", "D2", "D3", "D4", "D5\nK=1000", "D5\nK=10",
          "D5\nK=2", "D6\nR=2", "D6\nR=16", "D6\nR=256")
METRICS = ("elapsed_ms", "throughput_kps", "mem_peak_bytes", "key_comparisons",
           "array_reads", "array_writes", "run_count", "avg_run_len")


def trial_key(row):
    return (str(row.get("run_id", "run_main")),
            str(row.get("algorithm", row.get("algo"))).lower(),
            row["dataset"], str(row["n"]), str(row.get("k") or ""),
            str(row.get("runs") or ""), str(row["seed"]), row["mode"])


def group_key(row):
    return (row["algorithm"], row["dataset"], int(row["n"]),
            row["k"], row["runs"], row["mode"])


def audit(raw, config, environment):
    configs = json.loads(config.read_text(encoding="utf-8"))
    env = json.loads(environment.read_text(encoding="utf-8"))
    if env.get("raw_csv_sha256") and hashlib.sha256(raw.read_bytes()).hexdigest() != env["raw_csv_sha256"]:
        raise ValueError("Raw CSV changed after the measurement manifest was finalized")
    with raw.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    expected = {trial_key(c): c for c in configs}
    keys = [trial_key(r) for r in rows]
    if len(expected) != len(configs) or len(keys) != len(set(keys)):
        raise ValueError("Duplicate trial configuration or result")
    if set(keys) != set(expected):
        raise ValueError(f"Incomplete matrix: {len(keys)}/{len(expected)} trials")
    for name, wanted in env["source_files_sha256"].items():
        actual = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        if actual != wanted:
            raise ValueError(f"Measured source changed: {name}")
    inputs = defaultdict(list)
    statuses = Counter()
    for r in rows:
        if not r["code_commit"] or not env["source_commit"].startswith(r["code_commit"]):
            raise ValueError("Wrong source revision")
        for field in ("machine_id", "python_version"):
            if r[field] != env[field]:
                raise ValueError(f"Mixed {field}")
        if r["generator_version"] != GENERATOR_VERSION:
            raise ValueError("Different generator version")
        if r["rq"] != expected[trial_key(r)]["rq"]:
            raise ValueError("Research-question mapping mismatch")
        if r["status"] not in ("ok", "wrong", "timeout", "oom", "crash"):
            raise ValueError("Unknown status")
        statuses[r["status"]] += 1
        inputs[(r["dataset"], int(r["n"]), r["k"], r["runs"], int(r["seed"]))].append(r)
    for (ds, n, k, runs, seed), records in inputs.items():
        values = generate(ds, n, seed, k=int(k) if k else None,
                          runs=int(runs) if runs else None)
        # Independent encoding and recurrence, not the worker checksum helpers.
        digest = hashlib.sha256()
        for x in values:
            digest.update(struct.pack("<I", x))
        sha = digest.hexdigest()
        check = 0
        for x in sorted(values):
            check = ((check << 5) - check + x) & ((1 << 64) - 1)
        for r in records:
            if r["input_sha256"] and r["input_sha256"] != sha:
                raise ValueError("Input checksum mismatch")
            if r["status"] != "ok":
                continue
            if (r["input_sha256"] != sha or r["oracle_match"] != "True"
                    or r["output_check"] != str(check)):
                raise ValueError("Successful row lacks a matching oracle")
            if r["phase"] != "validate" or r["error_type"]:
                raise ValueError("Successful row has inconsistent validation state")
            if r["mode"] == "time":
                ms = float(r["elapsed_ms"])
                if not math.isfinite(ms) or ms <= 0 or r["mem_peak_bytes"]:
                    raise ValueError("Invalid timing result")
                if not math.isclose(float(r["throughput_kps"]), n/ms, rel_tol=.005, abs_tol=.01):
                    raise ValueError("Throughput units do not match")
            elif r["mode"] == "mem":
                if int(r["mem_peak_bytes"]) < 0 or r["elapsed_ms"]:
                    raise ValueError("Invalid memory result")
            elif r["elapsed_ms"] or r["mem_peak_bytes"]:
                raise ValueError("Count mode contains timing/memory")
            if r["mode"] == "count" and r["algorithm"] == "radix":
                if (int(r["array_reads"]) != 20*n+2040
                        or int(r["array_writes"]) != 17*n+2044):
                    raise ValueError("Radix operation counts do not match the reviewed code")
    grouped = defaultdict(list)
    for r in rows:
        grouped[group_key(r)].append(r)
    summary = []
    for key, samples in sorted(grouped.items()):
        if {r["seed"] for r in samples} != SEEDS or len(samples) != 3:
            raise ValueError("Missing or repeated seed")
        good = [r for r in samples if r["status"] == "ok"]
        result = dict(zip(("algorithm", "dataset", "n", "k", "runs", "mode"), key))
        result.update(n_total=3, n_ok=len(good), complete=len(good)==3,
                      statuses=json.dumps(dict(Counter(r["status"] for r in samples)), sort_keys=True))
        for metric in METRICS:
            vals = [float(r[metric]) for r in good if r.get(metric) not in ("", None)]
            for suffix, fn in (("median", statistics.median), ("min", min), ("max", max)):
                result[f"{metric}_{suffix}"] = fn(vals) if vals else ""
        summary.append(result)
    return rows, summary, dict(trials=len(rows), statuses=dict(statuses),
                               regenerated_inputs=len(inputs), groups=len(summary),
                               complete_groups=sum(r["complete"] for r in summary))


def make_outputs(rows, summary, checked, folder):
    folder.mkdir(parents=True, exist_ok=True)
    figs = folder / "figures"
    figs.mkdir(exist_ok=True)
    index = {(r["algorithm"], r["dataset"], r["n"], r["k"], r["runs"], r["mode"]): r for r in summary}

    def cell(algo, n, mode, family=("D1", "", "")):
        ds, k, runs = family
        return index[(algo, ds, n, k, runs, mode)]

    def number(algo, n, mode="time", family=("D1", "", "")):
        r = cell(algo, n, mode, family)
        field = "elapsed_ms" if mode == "time" else "mem_peak_bytes"
        return float(r[field+"_median"]) if r["complete"] else float("nan")

    tex = ["% Generated from audited CSV by scripts/analyze_ngan.py. Do not edit numbers."]
    def macro(name, value):
        tex.append("\\newcommand{\\"+name+"}{"+str(value)+"}")
    for name, value in (("TrialCount", checked["trials"]), ("OkCount", checked["statuses"].get("ok", 0)),
                        ("InputCount", checked["regenerated_inputs"]), ("GroupCount", checked["groups"]),
                        ("CompleteCount", checked["complete_groups"])):
        macro(name, value)
    macro("FailureCount", checked["trials"] - checked["statuses"].get("ok", 0))
    for algo in BASIC:
        prefix = algo.capitalize()
        macro(prefix+"TimeMillion", f"{number(algo,1000000):,.2f}")
        macro(prefix+"MemMillion", f"{number(algo,1000000,'mem')/1048576:.6f}")
        macro(prefix+"Growth", f"{number(algo,1000000)/number(algo,10000):.1f}")
    macro("MergeBytesPerElement", f"{number('merge',1000000,'mem')/1000000:.3f}")
    for ds, label in (("D1", "Random"), ("D2", "Sorted"), ("D4", "Reverse")):
        base = number("timsort-noA", 1000000, family=(ds,"",""))
        adaptive = number("timsort", 1000000, family=(ds,"",""))
        macro("RunGain"+label, f"{100*(base-adaptive)/base:.1f}")
    for n,label in ((100000,"Small"),(1000000,"Large")):
        delta = [100*(number("timsort-noA", n, family=f)-number("timsort", n, family=f))
                 / number("timsort-noA", n, family=f) for f in FAMILIES]
        macro("RunGain"+label+"Min", f"{min(delta):.1f}")
        macro("RunGain"+label+"Max", f"{max(delta):.1f}")
    table = []
    for n in SIZES:
        values = [f"{n:,}"]
        for algo in BASIC:
            r = cell(algo, n, "mem")
            if r["n_ok"]:
                med,low,high = [r["mem_peak_bytes_"+s]/1024 for s in ("median","min","max")]
                text = f"{med:,.2f} [{low:,.2f}, {high:,.2f}]"
            else:
                text = "--"
            if not r["complete"]:
                text += f" ({r['n_ok']}/3)"
            values.append(text)
        table.append(" & ".join(values)+r" \\")
    macro("MemoryTableRows", "\n".join(table))
    outcomes=[]
    for rq in ("RQ1", "RQ2", "RQ3"):
        selected=[r for r in rows if rq in r["rq"].split("+")]
        counts=Counter(r["status"] for r in selected)
        outcomes.append(f"{rq} & {len(selected)} & {counts['ok']} & {len(selected)-counts['ok']}"+r" \\")
    macro("CoverageTableRows", "\n".join(outcomes))
    counts_table=[]
    for algo in BASIC:
        fields=[algo.capitalize()]
        for n in (10000,1000000):
            item=cell(algo,n,"count")
            for metric in ("key_comparisons","array_reads","array_writes"):
                value=item[metric+"_median"]
                fields.append(f"{value:,.0f}" if item['complete'] and value!="" else "--")
        counts_table.append(" & ".join(fields)+r" \\")
    macro("CountTableRows", "\n".join(counts_table))
    winners=[]
    for f in FAMILIES:
        ds,k,r=f
        label=ds+(" K="+k if k else " R="+r if r else "")
        ranked=sorted((number(a,1000000,family=f),a) for a in BASIC)
        if all(math.isfinite(v) for v,a in ranked):
            winners.append(f"{label} & {ranked[0][1].capitalize()} & {ranked[0][0]:,.2f} & {ranked[-1][0]/ranked[0][0]:.2f}"+r" \\")
    macro("DistributionTableRows", "\n".join(winners))
    rq3=[]
    for f in FAMILIES:
        ds,k,r=f
        label=ds+(" K="+k if k else " R="+r if r else "")
        values=[label]
        for algo in ("quick","merge","timsort","timsort-noA","lib-sorted"):
            item=cell(algo,1000000,"time",f)
            values.append(f"{number(algo,1000000,family=f):,.2f}" if item["complete"]
                          else f"-- ({item['n_ok']}/3)")
        rq3.append(" & ".join(values)+r" \\")
    macro("AdaptiveTableRows", "\n".join(rq3))
    mechanism=[]
    for f in (FAMILIES[0],FAMILIES[1],FAMILIES[3],FAMILIES[7]):
        ds,k,r=f
        label=ds+(" R="+r if r else "")
        for algo,display in (("timsort","Adaptive"),("timsort-noA","noA")):
            c=cell(algo,1000000,"count",f)
            memory=cell(algo,1000000,"mem",f)
            comparisons=f"{c['key_comparisons_median']:,.0f}" if c["complete"] else "--"
            run_count=f"{c['run_count_median']:,.0f}" if c["complete"] and c['run_count_median']!="" else "--"
            peak=f"{memory['mem_peak_bytes_median']/1048576:.6f}" if memory["complete"] else "--"
            mechanism.append(f"{label} & {display} & {comparisons} & {run_count} & {peak}"+r" \\")
    macro("MechanismTableRows", "\n".join(mechanism))
    (folder / "results_generated.tex").write_text("\n".join(tex)+"\n",encoding="utf-8")

    memory_lines = [
        "# RQ1 — Bộ nhớ phụ từ thực nghiệm đã kiểm tra", "",
        "Phần Ngân; Codex hỗ trợ chạy, đối chiếu và viết. Không thay xác nhận review của My.", "",
        "Nguồn: `results/raw/ngan_20261029.csv`, mã nguồn `c73bc10`, generator 1.1.0, "
        "CPython 3.12.14. Môi trường và SHA-256 từng tệp ở "
        "`results/environment_ngan_20261029.json`. Máy đo thực tế là máy phát triển "
        "WIN-N3L18IBM8GL; không nhận đây là máy chính của Hải.", "",
        "Mỗi ô là median [min, max] trên seed 2026/2027/2028, đơn vị byte. "
        "Bộ nhớ đo trong tiến trình riêng: tracing ngay trước sort và tắt trước oracle. "
        "Input và bản sao làm việc được chuẩn bị trước tracing. Đây là đỉnh cấp phát "
        "bổ sung, không phải RSS hoặc tổng RAM.", "",
        "| N | Quick | Merge | Heap | Radix |", "|---:|---:|---:|---:|---:|",
    ]
    for n in SIZES:
        fields = [f"{n:,}"]
        for algo in BASIC:
            r=cell(algo,n,"mem")
            if r["n_ok"]:
                values=[int(r["mem_peak_bytes_"+s]) for s in ("median","min","max")]
                fields.append(f"{values[0]:,} [{values[1]:,}, {values[2]:,}] ({r['n_ok']}/3)")
            else:
                fields.append("Không hoàn thành (0/3)")
        memory_lines.append("| "+" | ".join(fields)+" |")
    memory_lines += ["", "## Diễn giải", "",
        f"Ở N=1.000.000, Merge có median {number('merge',1000000,'mem'):,.0f} byte "
        f"({number('merge',1000000,'mem')/1048576:.3f} MiB), tương đương "
        f"{number('merge',1000000,'mem')/1000000:.6f} byte/phần tử theo phép đo này. "
        "Kết quả phù hợp với một mảng phụ N tham chiếu và chi phí nhỏ hơn của "
        "biến/đệ quy. Buffer không sao chép toàn bộ đối tượng số nguyên. "
        "Không dùng byte/phần tử này như hằng số cho mọi bản Python.", "",
        f"Heap có median {number('heap',1000000,'mem'):,.0f} byte ở N=1.000.000. "
        "O(1) bộ nhớ phụ không có nghĩa mem_peak_bytes bằng 0. Quick vẫn cần "
        "trạng thái đệ quy; tracemalloc không đo đầy đủ mọi vùng stack/native allocation.", "",
        f"Radix có median {number('radix',1000000,'mem'):,.0f} byte ở N=1.000.000. "
        "Bản triển khai dùng output N phần tử, count 256 ô và copy-back bằng slice. "
        "Đỉnh đo bao gồm cấp phát của cách cài đặt này; không thể kết luận Radix "
        "là O(1) vì sửa trực tiếp danh sách đầu vào.", "",
        "Ba seed là ba đầu vào khác nhau, không phải ba lần timing cùng một đầu vào. "
        "Min=max ở một số ô thể hiện bộ cấp phát đạt cùng đỉnh trên các lượt đã chạy; "
        "không chứng minh mọi đầu vào hoặc mọi máy đều dùng đúng số byte đó.", "",
        "## Kiểm chứng và tái tạo", "",
        "`python -B -m scripts.analyze_ngan --audit-only` kiểm tra ma trận, seed, "
        "nhận dạng mã/máy, SHA-256 đầu vào, checksum oracle độc lập, throughput "
        "và bộ đếm Radix. Worker đã so sánh toàn bộ đầu ra với sorted(input); "
        "checksum trong CSV không thay thế phép so sánh đó.", "",
        "`python -B -m scripts.analyze_ngan` tái tạo summary CSV, phần này, bảng "
        "LaTeX và hình trong `paper/ieee/figures/`. Hình bộ nhớ RQ1 là "
        "`paper/ieee/figures/rq1_memory.pdf`; summary mọi mode ở "
        "`results/summary/ngan_20261029.csv`.",
    ]
    (folder.parent / "rq1_memory.md").write_text("\n".join(memory_lines)+"\n",encoding="utf-8")

    rq2_lines=["# RQ2 — Phân tích từ ma trận đo thực tế", "",
        "Chủ RQ2: Hải và Thiện. Ngân tổng hợp với hỗ trợ Codex sau khi chạy và audit. "
        "Bản này thay bản nháp dẫn rq2_pilot.csv không có trong repo; không sử dụng "
        "các số của bảng cũ.", "",
        "Nguồn: `results/raw/ngan_20261029.csv`, commit `c73bc10`, CPython 3.12.14, "
        "generator 1.1.0, máy phát triển WIN-N3L18IBM8GL. Seed 2026/2027/2028; "
        "time/mem/count chạy riêng. Chi tiết mọi mode, min/max và n_ok nằm ở "
        "`results/summary/ngan_20261029.csv`. Mọi kết luận dưới đây chỉ áp dụng "
        "các bản triển khai và môi trường đã đo.", ""]
    for n in (100000,1000000):
        rq2_lines += [f"## Thời gian ở N = {n:,}", "",
            "Đơn vị ms, mỗi ô median [min, max] từ ba seed thành công. "
            "Nếu thiếu lượt thành công, ô sẽ ghi n_ok/3 và không dùng để xếp hạng.", "",
            "| Dữ liệu | Quick | Merge | Heap | Radix |", "|---|---:|---:|---:|---:|"]
        for f in FAMILIES:
            ds,k,r=f
            label=ds+(" K="+k if k else " R="+r if r else "")
            fields=[label]
            for algo in BASIC:
                item=cell(algo,n,"time",f)
                if item["complete"]:
                    med,low,high=[item['elapsed_ms_'+s] for s in ('median','min','max')]
                    fields.append(f"{med:.2f} [{low:.2f}, {high:.2f}]")
                else:
                    fields.append(f"Chưa đủ ({item['n_ok']}/3)")
            rq2_lines.append("| "+" | ".join(fields)+" |")
        rad_times=[number('radix',n,family=f) for f in FAMILIES]
        heap_memory=[number('heap',n,'mem',f) for f in FAMILIES]
        rad_memory=[number('radix',n,'mem',f) for f in FAMILIES]
        rq2_lines += ["",
            f"Median thời gian Radix giữa các phân phối nằm trong khoảng "
            f"{min(rad_times):.2f}–{max(rad_times):.2f} ms. "
            f"Median cấp phát phụ của Heap là {min(heap_memory):,.0f}–{max(heap_memory):,.0f} byte, "
            f"Radix {min(rad_memory):,.0f}–{max(rad_memory):,.0f} byte. "
            "Khoảng này mô tả các median giữa phân phối, không phải khoảng tin cậy.", ""]
    rq2_lines += ["## Bộ đếm và kết luận có điều kiện", "",
        "Với N >= 2, code Radix hiện tại đếm reads = 20N + 2040 và "
        "writes = 17N + 2044. N=100.000 cho 2.002.040 lần đọc và 1.702.044 lần ghi; "
        "N=1.000.000 cho 20.002.040 lần đọc và 17.002.044 lần ghi. Trình audit kiểm "
        "tra mọi dòng Radix count; test độc lập quan sát đường sort bình thường "
        "để đối chiếu, gồm buffer và copy-back. Đây là truy cập phần tử logic, "
        "không phải số truy cập RAM hoặc mọi thao tác nội bộ CPython.", "",
        "Số lượt quét cố định không làm thời gian bất biến. D5 có thể giảm thời "
        "gian thực tế dù số truy cập logic Radix không đổi. Không quy kết nhân "
        "quả cho cache hay entropy khi chưa đo trực tiếp các cơ chế đó. Heap "
        "có bộ nhớ phụ O(1), không phải 0 byte. Radix dùng buffer N phần tử nên "
        "có bộ nhớ phụ O(N). Việc sửa danh sách đầu vào không thay đổi kết luận này.", "",
        "Không có cơ sở từ thí nghiệm này để tuyên bố thuật toán tối ưu cho "
        "mọi pipeline AI hoặc hệ nhúng. Dữ liệu là mô phỏng đặc điểm thứ tự; "
        "không đo hệ thống AI đầu cuối. Dòng lib-sorted thuộc ma trận RQ3, "
        "không được tự thêm vào RQ2 như đã có trong thiết kế 720 lượt.", "",
        "Tái tạo: `python -B -m scripts.analyze_ngan`; kiểm tra độc lập không vẽ: "
        "`python -B -m scripts.analyze_ngan --audit-only`. Hình so sánh ở "
        "`paper/ieee/figures/rq2_relative_time.pdf`; paper tổng hợp ở `paper/ieee/main.tex`.",
    ]
    (folder.parent / 'rq2_analysis.md').write_text('\n'.join(rq2_lines)+'\n',encoding='utf-8')

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    plt.rcParams.update({"font.family":"DejaVu Sans", "font.size":8,
                         "axes.labelsize":8, "legend.fontsize":7,
                         "xtick.labelsize":7,"ytick.labelsize":7,
                         "pdf.fonttype":42, "savefig.bbox":"tight"})
    colors={"quick":"#0072B2","merge":"#D55E00","heap":"#009E73","radix":"#CC79A7"}
    for mode,filename,ylabel,scale in (("mem","rq1_memory.pdf","Additional allocation (KiB)",1024),
                                     ("time","rq1_time.pdf","Sort time (ms)",1)):
        fig,ax=plt.subplots(figsize=(3.45,2.45))
        metric="mem_peak_bytes" if mode=="mem" else "elapsed_ms"
        for algo in BASIC:
            rs=[cell(algo,n,mode) for n in SIZES]
            med=np.array([r[metric+"_median"]/scale if r["complete"] else np.nan for r in rs])
            lo=np.array([r[metric+"_min"]/scale if r["complete"] else np.nan for r in rs])
            hi=np.array([r[metric+"_max"]/scale if r["complete"] else np.nan for r in rs])
            ax.plot(SIZES,med,marker={"quick":"o","merge":"s","heap":"^","radix":"D"}[algo],
                    markersize=3,label=algo.capitalize(),color=colors[algo])
            ax.fill_between(SIZES,lo,hi,color=colors[algo],alpha=.12)
        ax.set(xscale="log",yscale="log",xlabel="Number of elements N",ylabel=ylabel)
        ax.grid(alpha=.2,which="major");ax.legend(ncol=2)
        fig.tight_layout();fig.savefig(figs/filename);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(7.05,2.65),sharey=True)
    matrices=[]
    for n in (100000,1000000):
        data=np.array([[number(a,n,family=f) for f in FAMILIES] for a in BASIC])
        matrices.append(data/np.nanmin(data,axis=0))
    color_max=max(4,max(np.nanmax(matrix) for matrix in matrices))
    for ax,n,relative in zip(axes,(100000,1000000),matrices):
        ax.imshow(relative,aspect="auto",cmap="YlOrRd",vmin=1,vmax=color_max)
        for i in range(4):
            for j in range(10):
                ax.text(j,i,f"{relative[i,j]:.1f}",ha="center",va="center",fontsize=6,
                        color="white" if relative[i,j] > 1+.6*(color_max-1) else "black")
        ax.set_xticks(range(10),LABELS,fontsize=6)
        ax.set_yticks(range(4),[a.capitalize() for a in BASIC])
        ax.set_title(f"N = {n:,}");ax.set_xlabel("Data configuration")
    fig.tight_layout();fig.savefig(figs/"rq2_relative_time.pdf");plt.close(fig)
    fig,ax=plt.subplots(figsize=(3.45,2.6))
    x=np.arange(10)
    for offset,n,color in ((-.19,100000,"#0072B2"),(.19,1000000,"#D55E00")):
        gains=[100*(number("timsort-noA",n,family=f)-number("timsort",n,family=f))
               /number("timsort-noA",n,family=f) for f in FAMILIES]
        ax.bar(x+offset,gains,width=.36,label=f"N={n:,}",color=color,
               hatch="" if n==100000 else "//")
    ax.axhline(0,color="black",linewidth=.6)
    ax.set_xticks(x,LABELS,fontsize=6,rotation=45,ha="right")
    ax.set_ylabel("Time reduction relative to noA (%)")
    ax.legend();ax.grid(axis="y",alpha=.2)
    fig.tight_layout();fig.savefig(figs/"rq3_ablation.pdf");plt.close(fig)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--raw",type=Path,default=ROOT/"results/raw/ngan_20261029.csv")
    p.add_argument("--config",type=Path,default=ROOT/"bench/configs.json")
    p.add_argument("--environment",type=Path,default=ROOT/"results/environment_ngan_20261029.json")
    p.add_argument("--paper",type=Path,default=ROOT/"paper/ieee")
    p.add_argument("--audit-only",action="store_true")
    a=p.parse_args()
    rows,summary,checked=audit(a.raw,a.config,a.environment)
    print(json.dumps(checked,indent=2))
    if a.audit_only:
        return
    out=ROOT/"results/summary/ngan_20261029.csv"
    out.parent.mkdir(exist_ok=True)
    with out.open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(summary[0]));writer.writeheader();writer.writerows(summary)
    make_outputs(rows,summary,checked,a.paper)


if __name__=="__main__":
    main()
