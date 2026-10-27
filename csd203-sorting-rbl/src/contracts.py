"""Hợp đồng dùng chung. Không bật instrumentation trong sort(a)."""
METRIC_FIELDS = ("key_comparisons", "array_reads", "array_writes", "run_count", "avg_run_len")
def empty_metrics():
    return dict.fromkeys(METRIC_FIELDS)
