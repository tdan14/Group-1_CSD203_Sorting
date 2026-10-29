# Research Question 1 (RQ1): Execution Time Analysis & Hypotheses

> **Compilation note, 2026-10-30:** The hypotheses below are retained as the
> original predictions, not accepted conclusions. The measured N=10,000 D1
> ranking contradicts H1.2. Neither the predicted 150x growth nor the 15–40x
> library gap follows automatically from asymptotic complexity. The official
> RQ1 matrix contains only Quick/Merge/Heap/Radix; library trials belong to RQ3
> at N=100,000 and 1,000,000. The final paper uses only available measured
> configurations. Memory analysis: `paper/rq1_memory.md`; combined results:
> `paper/ieee/main.tex` and the audited CSV identified there.

**Focus:** Scaling behavior of baseline sorting algorithms on large uniform random data.  
**Lead Authors:** My (Time & Throughput Lead), Ngan (Memory Lead).  
**Algorithms Evaluated:** `quick`, `merge`, `heap`, `radix` (with `lib-sorted` as external baseline).  
**Dataset:** D1 (Uniform random integers in $[0, 2^{31} - 1]$).  
**Scale Matrix:** $N \in \{10{,}000;\; 50{,}000;\; 100{,}000;\; 500{,}000;\; 1{,}000{,}000\}$.  
**Repetitions:** 3 runs over official seeds (2026, 2027, 2028) on Hai's primary benchmark machine.

---

## 1. Research Question Statement

> **RQ1:** How do execution time, throughput, and auxiliary memory of the four foundational sorting algorithms (Quick, Merge, Heap, Radix) scale as input size $N$ increases from $10^4$ to $10^6$ on uniform random data in a pure CPython environment?

---

## 2. Theoretical Hypotheses (Formulated Prior to Empirical Measurement)

### Hypothesis H1.1 (Growth Trajectory & Asymptotic Gradient)
- As $N$ expands by a factor of 100 (from $10^4$ to $10^6$), the execution time of comparison-based algorithms (`quick`, `merge`, `heap`) will grow strictly according to $\Theta(N \log N)$ (approximately a $\approx 150\times$ increase, since $100 \times \frac{\log 10^6}{\log 10^4} = 100 \times 1.5 = 150$).
- Radix Sort (LSD 4 passes, 8 bits per radix) exhibits a linear theoretical time bound $\mathcal{O}(4N) = \mathcal{O}(N)$. Consequently, its execution time gradient with respect to $N$ will be flatter than that of comparison sorts.

### Hypothesis H1.2 (Relative Time Rankings in Pure Python)
- In a pure CPython 3.12 interpreter without JIT or vectorized acceleration:
  $$\text{Time}(\text{Quick}) < \text{Time}(\text{Merge}) < \text{Time}(\text{Heap}) < \text{Time}(\text{Radix})\quad (\text{for small to moderate } N)$$
- **Rationale:**
  1. **Quick Sort** executes in-place with Hoare partitioning, producing minimal array writes and maintaining strong spatial cache locality.
  2. **Merge Sort** requires copying elements into an auxiliary buffer of size $N$, incurring significant object reference allocation overhead in CPython.
  3. **Heap Sort** incurs non-sequential memory accesses during sift-down operations on the implicit binary heap, resulting in higher cache miss rates.
  4. **Radix Sort**, despite linear asymptotic complexity $\mathcal{O}(4N)$, suffers from interpreted Python loop overhead across 4 passes and 256 counting buckets per pass. At $N = 10^4$, this constant factor will render Radix slower than Quick Sort; however, at $N = 10^6$, Radix throughput will converge closer to comparison algorithms as linear scaling outpaces logarithmic scaling.

### Hypothesis H1.3 (Baseline Comparison with `lib-sorted`)
- `lib-sorted` (CPython's internal Timsort written in optimized C) will operate as an empirical performance ceiling, running approximately $15\times$ to $40\times$ faster than pure Python implementations due to compiled machine code execution and lack of Python bytecode dispatch overhead.

---

## 3. Metric Definitions and Analytical Guidelines

When benchmark CSVs are delivered by Hai (Milestone D8–D10), My will process the results using the standardized pipeline:

### A. Throughput Metric
$$\text{throughput\_kps} = \frac{N}{\text{elapsed\_ms}} \quad (\text{kilo-elements / second})$$

### B. Speedup Ratio
$$\text{Speedup}_{\text{Quick}} = \frac{\text{elapsed\_ms}(\text{Algorithm } X)}{\text{elapsed\_ms}(\text{Quick})}$$

### C. Data Integrity and Verification
- Every measurement entry must satisfy:
  - $\text{status} = \text{'ok'}$
  - $\text{oracle\_match} = \text{True}$ (identical to `sorted(D1)`)
  - $\text{output\_check} = h_N$, where:
    $$h_0 = 0, \quad h_{i} = (31 \cdot h_{i-1} + x_i) \pmod{2^{64}}$$

### D. Statistical Aggregation Rules
1. **Summary Statistics:** Report `median`, `min`, `max`, and `ok_count` across the 3 seeds for each $(N, \text{algorithm})$ tuple.
2. **Missing/Error Records:** If any run encounters `timeout`, `crash`, or `oom`, the report must explicitly state the success count (e.g., "2/3 ok"). Never report the median of a partial set as if it were a full 3-run sample.
3. **Environment Isolation:** Do not merge datasets originating from different machines (`machine_id`) or different commits (`code_commit`).

---

## 4. Visualizations to Generate (Milestones D11–D12)

1. **Figure 1 (Time Scaling):** Dual-axis or Log-Log plot of `elapsed_ms` vs. $N$ across the four algorithms and `lib-sorted`.
2. **Figure 2 (Throughput Profile):** Grouped bar chart of `throughput_kps` at each magnitude of $N$, illustrating throughput stability.
3. **Traceability:** Each figure generated in `results/figures/` will be directly reproducible via `bench/plot_rq1.py` referencing `results/raw/rq1_benchmark.csv`.
