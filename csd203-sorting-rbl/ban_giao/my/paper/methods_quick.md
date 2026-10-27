# Section: Methods — Quick Sort Implementation

**Author:** My (CSD203 RBL Research Group)  
**Target Paper:** IEEE 2-Column Conference Format (CSD203 FA26)  
**Primary Reference:** C. A. R. Hoare, "Quicksort," *The Computer Journal*, vol. 5, no. 1, pp. 10–16, 1962. doi: 10.1093/comjnl/5.1.10.

---

## 1. Algorithmic Design and Architectural Overview

Quick Sort is an archetypal divide-and-conquer algorithm designed for high-throughput in-place comparison-based sorting. In our experimental framework, we strictly adhere to Hoare's classical partitioning scheme combined with a **Median-of-Three (MOT)** pivot selection strategy, implemented entirely in pure standard-library Python (CPython 3.12 target).

In accordance with project constraints:
1. **In-place Execution:** Sorting operates directly on the input list `a` without auxiliary buffers.
2. **No Insertion Sort Cutoff:** Small partitions are not handed over to Insertion Sort, isolating the pure asymptotic and constant-factor characteristics of Quick Sort across all recursion depths.
3. **Unified Execution Pathway:** Both standard execution (`sort`) and metric profiling (`sort_counted`) share an identical recursive call graph to prevent algorithmic divergence.
4. **Standard Stack Handling:** Recursion limit modifications via `sys.setrecursionlimit()` are explicitly forbidden; any excessive stack consumption is treated as a `crash`.

```
                    +------------------------------------+
                    |        Input Array a[lo..hi]       |
                    +------------------------------------+
                                      |
                     [Step 1: Median-of-Three Selection]
                                      |
                 +--------------------+--------------------+
                 | a[lo] <= a[mid] <= a[hi]                |
                 | Pivot fixed at a[mid]                   |
                 +-----------------------------------------+
                                      |
                        [Step 2: Hoare Partitioning]
                                      |
             Two-pointer scan (i from lo-1, j from hi+1)
             Invariants: a[lo..j] <= pivot, a[j+1..hi] >= pivot
                                      |
                        +-------------+-------------+
                        |                           |
             Subarray a[lo..j]             Subarray a[j+1..hi]
             (Recursive Call)              (Recursive Call)
```

---

## 2. Mapping Mechanism to Implementation

Each theoretical component maps directly to modular primitives in [`src/quick.py`](file:///C:/Users/Admin/Desktop/CSD203/Lab/src/quick.py):

### A. Public Interfaces
- **`sort(a: list) -> None`**: The production-grade sorting interface. Invokes the internal recursive engine with `cnt=None`. Performs zero bounds validation, memory allocation, logging, or metric tracking within the measurement perimeter.
- **`sort_counted(a: list) -> dict`**: The telemetry profiling interface. Initializes operational counters (`key_comparisons`, `array_reads`, `array_writes`) and returns a structured record matching project schema. `run_count` and `avg_run_len` are set to `None` as run detection is not applicable to Quick Sort.

### B. Pivot Selection: Median-of-Three (`_median_of_three`)
To mitigate worst-case $\mathcal{O}(N^2)$ degradation on monotonic (D2, D4) or clustered data, the pivot is chosen as the median of the first, middle, and last elements:
$$\text{mid} = \lfloor(\text{lo} + \text{hi}) / 2\rfloor$$
For subarrays of size $N \ge 3$ ($\text{hi} - \text{lo} \ge 2$), exactly three key comparisons sort $a[\text{lo}]$, $a[\text{mid}]$, and $a[\text{hi}]$ into non-decreasing order:
1. Compare and swap $(a[\text{lo}], a[\text{mid}])$ if $a[\text{lo}] > a[\text{mid}]$.
2. Compare and swap $(a[\text{mid}], a[\text{hi}])$ if $a[\text{mid}] > a[\text{hi}]$.
3. Compare and swap $(a[\text{lo}], a[\text{mid}])$ if $a[\text{lo}] > a[\text{mid}]$.

Crucially, **the pivot value is retained at $a[\text{mid}]$**. For two-element subarrays ($\text{hi} - \text{lo} = 1$), a single comparison ensures $a[\text{lo}] \le a[\text{hi}]$.

### C. Partitioning Scheme: Hoare (`_hoare_partition`)
Hoare's scheme initializes two roving pointers:
$$i \leftarrow \text{lo} - 1, \quad j \leftarrow \text{hi} + 1$$
In each iteration:
- Pointer $i$ advances rightward until $a[i] \ge \text{pivot}$.
- Pointer $j$ advances leftward until $a[j] \le \text{pivot}$.
- If $i < j$, elements $a[i]$ and $a[j]$ are exchanged.
- When $i \ge j$, pointer $j$ is returned as the partition index.

**Mathematical Guarantee against Infinite Recursion:**
Because the pivot is pinned at $a[\text{mid}]$ where $\text{lo} \le \text{mid} < \text{hi}$ and $a[\text{lo}] \le \text{pivot} \le a[\text{hi}]$:
- The pointer $i$ cannot advance beyond $\text{hi}$ because $a[\text{hi}] \ge \text{pivot}$.
- The pointer $j$ cannot retreat below $\text{lo}$ because $a[\text{lo}] \le \text{pivot}$.
- The returned index $j$ strictly satisfies $\text{lo} \le j < \text{hi}$.
Consequently, the partition $a[\text{lo}..j]$ contains at most $\text{hi} - \text{lo}$ elements, ensuring strict monotonic decrease in partition size and preventing infinite recursion on all inputs, including arrays with identical values (D5).

### D. Metric Instrumentation Primitives
Tracking is implemented via unified wrappers (`_read`, `_write`, `_swap`):
- **`key_comparisons`**: Recorded for every execution of `>` or `<` on element values, covering both MOT pivot determination (1 to 3 comparisons) and loop conditions ($a[i] < \text{pivot}$ and $a[j] > \text{pivot}$).
- **`array_reads`**: Incremented on each indexed access `a[idx]`.
- **`array_writes`**: Incremented on each assignment `a[idx] = val`.

---

## 3. Asymptotic Complexity and Resource Profiling

| Metric | Best Case | Average Case | Worst Case |
|---|---|---|---|
| **Time Complexity** | $\mathcal{O}(N \log N)$ | $\Theta(N \log N)$ | $\mathcal{O}(N^2)$ |
| **Key Comparisons** | $\approx N \log_2 N$ | $\approx 1.386 N \log_2 N$ | $\approx \frac{N^2}{2}$ |
| **Auxiliary Memory** | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ |
| **Call Stack Depth** | $\mathcal{O}(\log N)$ | $\mathcal{O}(\log N)$ | $\mathcal{O}(N)$ |
| **Stability** | No | No | No |

**Analytical Observations for RQ1:**
1. On uniform random permutations (D1), the expected recursive depth remains bounded within $2 \ln N \approx 1.386 \log_2 N$, requiring negligible call stack memory ($< 60$ frames for $N = 1,000,000$).
2. Unlike Merge Sort which mandates an auxiliary buffer of size $N$, Quick Sort operates strictly in-place with zero heap allocations during sorting.
3. The cache locality of Hoare's two-pointer scan yields minimal memory bus contention, anticipating competitive throughput ($N / \text{elapsed\_ms}$) on large scale datasets.
