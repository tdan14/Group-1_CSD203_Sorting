# Methods — Stable Top-down Merge Sort

Author: Ngân. Implementation: `src/merge.py`. Review by My: pending.

## Algorithm and implementation

The implementation uses recursive top-down Merge Sort with half-open intervals
`[lo, hi)`. Each interval of length at least two is divided at
`mid = (lo + hi) // 2`. The left and right intervals are sorted recursively and
then merged back into the original list. This is the standard top-down design;
the stable merge and reusable auxiliary storage can also be checked against
Sedgewick and Wayne's reference implementation [1].

For N >= 2, `sort(a)` allocates exactly one auxiliary list, `aux = [None] * N`,
before recursion. Every merge receives the same list. A merge copies only the
active interval into `aux`, then writes the merged sequence back into `a`.
Neither input slicing nor allocation of left/right sublists is used. Empty and
single-element inputs return immediately and require no auxiliary list.

At each merge step, the implementation reads the current left and right values.
It selects the right value only when `right_value < left_value`; otherwise it
selects the left value. Thus objects need only implement `__lt__`, which matches
the group's key-only stability test. There is no insertion-sort cutoff or
already-sorted shortcut in this implementation.

Mechanism-to-function mapping:

- Public timed entry and one-time allocation: `sort`.
- Recursive division: `_sort`.
- Stable merge using the shared buffer: `_merge`.
- Counted entry and allocation accounting: `sort_counted`.
- Counted recursive division and merge: `_sort_counted`, `_merge_counted`.

## Correctness and stability

An interval with at most one element is sorted. Inductively assume both child
intervals are sorted. Their smallest remaining elements are at the current
left/right cursors; writing the smaller one preserves the sorted output prefix.
Once a child is exhausted, the remaining elements of the other child can be
copied in order. Each input reference is written exactly once to the merged
interval, preserving its multiset.

Equivalent keys are taken from the left child first. Each child preserves its
own order by the induction hypothesis, and original left-child elements precede
original right-child elements. Consequently, equal keys retain their original
relative order across every merge. Stability assumes a consistent strict weak
ordering; the benchmark's integer keys meet this requirement.

## Complexity and memory interpretation for RQ1

For N >= 2, the recurrence is
`T(N) = T(floor(N/2)) + T(ceil(N/2)) + Theta(N)`.
Because all merges are executed even on already ordered input, this
implementation takes Theta(N log N) time on the benchmark families, assuming
constant-time key comparisons. The auxiliary list requires Theta(N) reference
slots; recursion adds O(log N) stack depth. Overall auxiliary space is Theta(N).

The buffer stores references to existing elements, not copies of integer
objects. Nevertheless, measured `mem_peak_bytes` also reflects Python
allocation overhead and temporary objects. It must not be replaced by a
theoretical fixed number of bytes per element. Similarly, describing Quick
Sort as having no auxiliary array does not make its recursion memory zero.

For the empirical RQ1 comparison, use D1 at N = 10,000; 50,000; 100,000;
500,000; 1,000,000 and seeds 2026/2027/2028 on the group's main measurement
machine. Measure memory in the worker's separate `mem` process; the input and
working copy are prepared before tracing starts. Report median/min/max,
successful-trial count, Python version, generator version, and code commit.
No empirical ranking or memory measurements are claimed in this Methods draft.

## Operation counting

The timed path contains no counter updates or counter conditionals. The counted
path follows the same recursive splits, key-comparison sequence and merge
decisions. `key_comparisons` counts each executed `<` between keys.
`array_reads` counts reads of elements from `a` and `aux`; `array_writes` counts
writes to either array, including the N initial auxiliary-slot writes.
Index comparisons, scalar assignments, recursion bookkeeping and changes to
the counter dictionary are excluded. `run_count` and `avg_run_len` are `None`.
For N < 2, all three operation counters are zero.

## Verification and limits

`tests/test_merge.py` checks the five required edge cases, 1,000 deterministic
random cases covering all ten D1–D6 parameter configurations, odd lengths and
larger inputs, and stability on 1,000 key-only records for both execution paths.
It also checks identical comparison traces, observed comparison counts, exact
counts on two-element inputs, shared-buffer reuse and absence of input slicing.
These tests establish correctness for the exercised cases; they do not replace
the official three-seed performance experiments or My's independent review.

## References

[1] R. Sedgewick and K. Wayne, *Algorithms*, 4th ed., Addison-Wesley, 2011,
Section 2.2. Author-maintained reference source, consulted 2026-10-28:
https://github.com/kevin-wayne/algs4/blob/master/src/main/java/edu/princeton/cs/algs4/Merge.java.

The course also requires M. T. Goodrich, R. Tamassia and M. H. Goldwasser,
*Data Structures and Algorithms in Python*, Wiley, 2013, Chapter 12. The group
should consult its course copy when finalizing Background and References;
no page-specific quotation from that book is claimed here.
