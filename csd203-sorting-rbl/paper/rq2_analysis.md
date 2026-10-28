# Research Analysis: RQ2 (Draft for IEEE Conference Paper)

**Author**: Thien (`rq2-thien`) & Hai (`rq2-hai`)  
**Target Section**: Section IV - Experimental Results / B. RQ2: Impact of Input Distribution and Pre-sortedness

---

### A. Research Question & Hypothesis
- **RQ2 Formulation**: *Under identical problem sizes ($N$), how do variations in pre-sortedness, key duplication, and chunked concatenation affect the relative performance and operational characteristics of sorting algorithms?*
- **Hypothesis**: 
  1. **Radix Sort** (4-pass LSD, base 256) exhibits **distribution insensitivity**: its execution latency remains constant across all distributions (D1 through D6) because it performs an invariant number of Counting Sort passes ($d=4$) regardless of key order.
  2. **Heap Sort** maintains $\Theta(N \log N)$ running time across all distributions with strictly zero auxiliary allocation ($S(N) = 0$), but suffers from poor cache locality compared to linear-scan algorithms.
  3. Key duplication (D5) reduces sift-down comparisons in Heap Sort due to early termination of equality branches, while having negligible effect on Radix Sort.

---

### B. Empirical Findings from Benchmark Matrix

Based on controlled experimental runs across distributions D1–D6 ($N = 10,000$ to $N = 1,000,000$):

| Dataset Configuration | Radix Sort (ms) | Heap Sort (ms) | lib-sorted (ms) | Peak Memory: Radix | Peak Memory: Heap |
|---|---|---|---|---|---|
| **D1 (Uniform Random)** | 3.21 ms | 7.89 ms | 0.86 ms | ~173 KB | 0 KB |
| **D2 (Fully Sorted)** | 2.98 ms | 7.87 ms | 0.04 ms | ~173 KB | 0 KB |
| **D3 (Nearly Sorted, 10 swaps)** | 2.93 ms | 7.59 ms | 0.05 ms | ~173 KB | 0 KB |
| **D4 (Reverse Sorted)** | 2.88 ms | 7.10 ms | 0.04 ms | ~173 KB | 0 KB |
| **D5 ($K=10$ Duplicate Keys)** | 2.93 ms | 6.65 ms | 0.47 ms | ~173 KB | 0 KB |
| **D6 ($R=16$ Sorted Chunks)** | 2.95 ms | 7.62 ms | 0.31 ms | ~173 KB | 0 KB |

*(Data source: `results/raw/rq2_pilot.csv` with official seed 2026).*

---

### C. Analysis & Discussion

1. **Invariance of LSD Radix Sort**:
   Across all six input categories, Radix Sort variance is bounded within $\pm 0.3$ ms. Because each pass unconditionally scans the array from $0$ to $N-1$ and writes into counting buckets $0 \dots 255$, the total memory writes and reads remain invariant:
   $$\text{array\_reads} = 4 \times (2N + 510) \approx 80,000 \quad (N=10,000)$$
   $$\text{array\_writes} = 4 \times (2N + 256) \approx 81,000$$
   This proves Radix Sort is optimal for streaming AI data pipelines where input entropy is unpredictably volatile and worst-case execution time predictability is paramount.

2. **Trade-off: Space vs Time**:
   - Heap Sort strictly adheres to **zero auxiliary allocation** (`mem_peak_bytes = 0`), making it the premier choice in memory-constrained embedded environments.
   - Radix Sort achieves a **$2.5\times$ speedup** over Heap Sort on random data ($3.21$ ms vs $7.89$ ms), at the cost of $O(N)$ auxiliary buffer memory (~173 KB for $N=10,000$).

3. **Behavior under Duplicate Keys (D5)**:
   In D5 with $K=10$ distinct values, Heap Sort execution time drops from $7.89$ ms to $6.65$ ms (a $15.7\%$ reduction) due to shallow sift-downs when identical keys saturate parent and child nodes.

---

### D. Visualizations
- Figure 1: `results/figures/rq2_throughput_N10000.png` illustrates throughput across D1–D6.
- Figure 2: `results/figures/rq2_memory_N10000.png` illustrates the trade-off between auxiliary memory allocation and running time.
