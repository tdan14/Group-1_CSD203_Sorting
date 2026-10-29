# Research Question 2 (RQ2): Hypotheses & Experimental Analysis Plan

> Technical clarification during Ngan's compilation (2026-10-30): fixed loop
> counts are distinguished from elapsed-time predictions; auxiliary complexity
> is distinguished from traced bytes. These corrections are not a claim of
> preregistration. Measured outcomes and the CSV source are in `rq2_analysis.md`.

**Focus:** Impact of data distribution, pre-sortedness, key duplication, and chunked batches on algorithmic performance.  
**Lead Authors:** Hai (`rq2-hai`) & Thien (`rq2-thien`).  
**Algorithms Evaluated:** `quick`, `merge`, `heap`, `radix`. The `lib-sorted` reference belongs to RQ3.
**Datasets Evaluated:** 
- D1 (Uniform random), D2 (Sorted), D3 (Nearly sorted, $N/1000$ swaps), D4 (Reverse sorted).
- D5 (Key duplication with $K \in \{1000, 10, 2\}$ distinct values).
- D6 (Concatenated sorted batches with $R \in \{2, 16, 256\}$ chunks).  
**Scale Matrix:** $N \in \{100{,}000;\; 1{,}000{,}000\}$.  
**Repetitions:** 3 runs over official seeds (2026, 2027, 2028). Total: 720 configurations for RQ2.

---

## 1. Research Question Statement

> **RQ2:** Under identical problem sizes ($N$), how do variations in pre-existing sortedness, degree of key duplication, and concatenated chunk structures alter the relative ranking, execution latency, peak memory, and operation counts of the four foundational algorithms?

---

## 2. Pre-Measurement Hypotheses

### Hypothesis H2.1 (Distribution Insensitivity of LSD Radix Sort)
- **Radix Sort** (4-pass LSD, base 256) executes the same logical array-access counts for fixed N across D1–D6. Its elapsed time and peak traced allocation must still be measured; they need not remain constant. A testable expectation is that prior sortedness does not remove any of its four passes.
- **Theoretical Basis:** The algorithm unconditionally executes $d=4$ passes of Counting Sort. In each pass, every element is scanned regardless of prior ordering:
  $$\text{array\_reads} = 4(5N + 510) = 20N + 2040,$$
  $$\text{array\_writes} = N + 4(4N + 511) = 17N + 2044 \quad (N\ge2).$$
  These formulas include output/count initialization according to the code's logical counting convention. They do not establish constant latency or optimality for a real pipeline.

### Hypothesis H2.2 (Behavior on Duplicate Keys — Dataset D5)
- When key cardinality drops ($K = 1000 \to 10 \to 2$):
  - **Quick Sort** with Hoare partitioning and median-of-3 pivot will see partition balance affected. While Hoare's scheme handles equal keys better than Lomuto's (halting on duplicates), deep recursion or redundant swaps may still impact performance compared to 3-way partitioning.
  - **Heap Sort** execution time will decrease on extreme duplicates ($K=2$) because many sift-down comparisons terminate early when child values match the current node value.
  - **Radix Sort** retains the same pass/access counts. Timing can change. In any byte pass, at most min(K, 256) buckets can be occupied; distinct full keys can share the same byte value.

### Hypothesis H2.3 (Behavior on Pre-Sorted and Chunked Data — D2, D3, D6)
- **Heap Sort** has an $O(N\log N)$ worst-case time bound and $O(1)$ auxiliary words, but does not explicitly detect natural runs. Whether it is slower than an adaptive implementation is a measured question. $O(1)$ does not imply zero traced bytes.
- **Merge Sort** maintains consistent $\Theta(N \log N)$ runtime and strict stability, with constant $O(N)$ auxiliary memory buffer allocation.
- **Quick** and **Heap** do not allocate an N-element auxiliary array; Quick still has recursion state. **Radix** and **Merge** both use $O(N)$ auxiliary storage. Their actual peaks depend on implementation and must be compared using the separate memory trials.

---

## 3. Analysis & Verification Protocol

- Measurement execution is strictly partitioned into `time`, `mem` (isolated `tracemalloc`), and `count` modes with a 60-second subprocess timeout.
- Metrics reported:
  - Throughput: $\text{throughput\_kps} = N / \text{elapsed\_ms}$.
  - Peak memory: $\text{mem\_peak\_bytes}$ recorded before oracle validation.
  - Operations: $\text{key\_comparisons}$ for Quick/Merge/Heap; $\text{array\_reads}$ and $\text{array\_writes}$ reported separately for Radix Sort.
- Visualizations generated via `bench.plot`:
  - `rq2_throughput_N{n}.png`: Grouped bar chart comparing throughput across D1–D6.
  - `rq2_memory_N{n}.png`: Peak auxiliary memory allocation across algorithms.
  - `rq2_operations_N{n}.png`: Comparison vs Array access breakdown.
