# Section: Limitations and Architectural Trade-offs — Quick Sort

**Author:** My (CSD203 RBL Research Group)  
**Target Paper:** IEEE 2-Column Conference Format (CSD203 FA26)  
**Context:** Analytical discussion complementing [`paper/methods_quick.md`](file:///C:/Users/Admin/Desktop/CSD203/Lab/paper/methods_quick.md) and [`src/quick.py`](file:///C:/Users/Admin/Desktop/CSD203/Lab/src/quick.py).

---

## 1. Overview

While Quick Sort equipped with Hoare partitioning and Median-of-Three (MOT) pivot selection demonstrates high empirical throughput on uniform random datasets (D1), several intrinsic theoretical and systemic constraints bound its applicability within real-world data pipelines. In accordance with the IEEE reporting standards and project guidelines, we explicitly delineate four critical limitations below.

---

## 2. In-Depth Analysis of Limitations

### A. Algorithmic Instability (Unstable Sorting)
- **Mechanistic Cause:** In Hoare's partitioning scheme (`_hoare_partition`, [`src/quick.py`](file:///C:/Users/Admin/Desktop/CSD203/Lab/src/quick.py#L69-L107)), pointers $i$ and $j$ scan inward from opposite boundaries, exchanging elements across long intervals via `_swap` without tracking their initial sequence.
- **Consequence:** Equal keys routinely invert their relative positions. Consequently, Quick Sort cannot serve multi-key ordering workflows (e.g., sorting logs chronologically and then grouping by category) without augmenting elements with explicit original index tags, which incurs additional $\mathcal{O}(N)$ auxiliary memory. In contrast, Merge Sort natively maintains stability.

### B. Worst-Case Recursion Depth and Stack Overflow Vulnerability
- **Theoretical Bound:** Although Median-of-Three pivot selection completely neutralizes quadratic degradation on monotonic sequences (D2, D4) by guaranteeing non-extreme pivots, adversarial inputs engineered against deterministic MOT can still induce asymmetric partitions. In the theoretical worst-case, partition depth degrades to $\mathcal{O}(N)$.
- **Empirical Constraint:** Under the strict project mandate forbidding artificial stack expansion (`sys.setrecursionlimit()`, `AI_LOG.md` Item #5), any execution exceeding CPython's default call stack limit (~1,000 frames) immediately terminates as a `crash` rather than completing. On uniform random data (D1), the expected recursive depth remains safe ($< 60$ frames at $N = 10^6$), but the vulnerability remains present under adversarial distributions.

### C. CPython Interpretation Overhead and CPU Cache Saturation
- **Interpreter Overhead:** Executing pure Python bytecode without JIT acceleration introduces significant interpreter dispatch overhead for every comparison (`_read`, `_cmp`) and array assignment (`_write`). This constant-factor overhead accounts for the substantial speedup ratio observed in compiled baselines (`lib-sorted`, running compiled C code $15\times$ to $40\times$ faster).
- **Memory Hierarchy Scaling:** As dataset size scales from $N = 10^4$ to $N = 10^6$ (representing $> 8\text{ MB}$ of 64-bit integer object pointers), element access surpasses CPU L1/L2 cache capacities and encroaches on shared L3 cache. Random access across two-pointer partitions induces non-trivial cache miss penalties, manifesting as a noticeable upward slope inflection on log-log execution curves at $N \ge 500,000$.

### D. Prohibition of Small Subarray Cutoff (Strict Baseline Constraint)
- **Design Mandate:** Production Quick Sort variants typically revert to Insertion Sort when subarray sizes drop below a threshold (e.g., $M \in [8, 16]$) to eliminate recursion and pivot overhead on small partitions. The project specification strictly bans this optimization (*"không chuyển sang Insertion Sort khi mảng nhỏ"*).
- **Performance Impact:** In our implementation, every base partition down to size 2 must execute the full Median-of-Three routine (1 to 3 comparisons) and allocate stack frames for both child partitions. For $N = 10^6$, approximately $5 \times 10^5$ leaf partitions are evaluated through recursive dispatch, amplifying interpreter call overhead on trivial arrays and slightly penalizing empirical throughput relative to hybrid sorters.
