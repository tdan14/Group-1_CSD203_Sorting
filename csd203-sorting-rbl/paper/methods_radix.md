# Methods: Radix Sort (Draft for IEEE Conference Paper)

**Author**: Thien (`rq2-thien`)  
**Target Section**: Section III - Algorithms and Implementations / Radix Sort

---

### A. Algorithmic Formulation of LSD Radix Sort

Radix Sort is a non-comparative sorting algorithm that sorts integer keys by grouping elements by individual digits or bytes, processing them from the least significant digit (LSD) to the most significant digit (MSD) \cite{goodrich2013}.

In this study, following the project specification for pure Python implementation on a 32-bit unsigned integer domain $[0, 2^{31} - 1]$, we implement **LSD Radix Sort with base $b = 256 = 2^8$**, requiring exactly $d = 4$ passes:
1. **Pass 0**: Byte 0 (bits 0–7): $\text{byte}_0(x) = (x \gg 0) \ \& \ 255$
2. **Pass 1**: Byte 1 (bits 8–15): $\text{byte}_1(x) = (x \gg 8) \ \& \ 255$
3. **Pass 2**: Byte 2 (bits 16–23): $\text{byte}_2(x) = (x \gg 16) \ \& \ 255$
4. **Pass 3**: Byte 3 (bits 24–31): $\text{byte}_3(x) = (x \gg 24) \ \& \ 255$

For each pass $k \in \{0, 1, 2, 3\}$, an **in-place stable sub-sorting algorithm**—specifically **Counting Sort**—is executed:
1. **Histogram Construction**: A frequency array $C$ of size $b = 256$ records occurrences of each byte value:
   $$C[v] = \sum_{j=0}^{N-1} \mathbb{I}(\text{byte}_k(A[j]) = v)$$
2. **Prefix Sum (Cumulative Offset)**: $C$ is transformed into running indices:
   $$C[v] \leftarrow C[v] + C[v - 1], \quad \forall v \in [1, 255]$$
3. **Stable Placement**: Elements are scanned in reverse order (from index $N - 1$ down to $0$) and placed into an auxiliary buffer $B[N]$ at offset $C[v] - 1$, decrementing $C[v]$ after each placement:
   $$B[--C[\text{byte}_k(A[j])]] = A[j]$$
   The backward scan guarantees that elements with identical byte values retain their relative order established in prior passes (stability requirement).
4. **Copy-back**: Elements from $B$ are copied back to $A$ so that subsequent passes operate directly on the partially sorted array.

---

### B. Theoretical Complexity Analysis

- **Time Complexity**: Each pass takes linear time $\Theta(N + b)$ to tally, scan, and reorder. Over $d = 4$ fixed passes, total time complexity is:
  $$T(N) = \Theta(d \cdot (N + b)) = \Theta(4 \cdot (N + 256)) = \Theta(N)$$
  Because $d = 4$ is constant, Radix Sort guarantees deterministic linear asymptotic runtime regardless of input distribution (D1–D6), rendering it insensitive to pre-existing sortedness.
- **Auxiliary Space Complexity**:
  $$S(N) = \Theta(N + b)$$
  composed of the auxiliary placement array $B$ of size $N$ and the frequency bucket array $C$ of size 256.
- **Key Comparisons**: As a distribution-based algorithm, Radix Sort performs **zero** key-to-key comparisons ($\text{key\_comparisons} = \text{None}$). Instead, computational effort is characterized by array memory access primitives ($\text{array\_reads}$ and $\text{array\_writes}$).

---

### References
- [goodrich2013] M. T. Goodrich, R. Tamassia, and M. H. Goldwasser, *Data Structures and Algorithms in Python*, John Wiley & Sons, 2013, Ch. 12, pp. 545–560.
