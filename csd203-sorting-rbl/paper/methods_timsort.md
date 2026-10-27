# Timsort with Powersort and the noA variant

The group implementation is written in pure Python. It uses natural run
detection, a computed minimum run length, stable binary insertion sort,
and Powersort to choose adjacent merges. Galloping is omitted under the
five-member project scope.

`minrun_length` repeatedly halves the input length until it is below 64,
retaining discarded low bits. `_count_run` detects nondecreasing or
strictly decreasing runs; only strictly decreasing runs are reversed.
Short runs are extended by `_binary_insertion`, which places equal keys
after existing equal keys.

`node_power` computes the first binary partition depth that separates
the normalized midpoints of adjacent runs. `_push_run` merges pending
boundaries with greater power before pushing the next run.
`_finish_merges` completes the remaining merges. The policy follows
Powersort as described by Munro and Wild and documented in CPython 3.12:
[CPython listsort notes](https://github.com/python/cpython/blob/3.12/Objects/listsort.txt),
[powerloop and stack policy](https://github.com/python/cpython/blob/3.12/Objects/listobject.c).

`_merge` copies the shorter run into a temporary list. Forward merging
takes the left item on equal keys; backward merging takes the right item
on equal keys. Together with stable insertion and strict descending-run
reversal, these choices preserve the relative order of equal keys.
Worst-case running time is O(N log N), with O(N) auxiliary storage.

The noA variant disables natural-run detection and sorts fixed minrun
blocks before applying the same merge policy. It shares minrun, insertion,
power calculation and merging with the natural-run version.

Counted functions reproduce the comparison sequence of the uninstrumented
functions. They report key comparisons; array-read and array-write fields
are not instrumented and remain null. Natural-run metrics describe runs
encountered by the actual scan before minrun extension. Their mean uses
the sum of those detected lengths, excluding unscanned sections absorbed
by extension. These metrics do not describe a separate full decomposition
of the original input. noA leaves natural-run fields null.

Validation includes edge cases, 1,000 generated inputs across D1–D6 for
all four entry points, stability on 1,000 records comparing only their
keys, identical comparison traces for plain/counted paths, midpoint-power
checks, and both merge-buffer directions. These are implementation checks;
no official RQ3 measurements or performance conclusions are supplied here.

AI assistance was used for this implementation and its tests. Member review
and individual explanation remain required before final submission.
