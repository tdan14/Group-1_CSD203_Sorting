"""Phan cua Dan: Timsort dung Powersort, khong co Galloping."""

READY = True
COUNTED_READY = True
NOA_READY = True
NOA_COUNTED_READY = True


def minrun_length(n):
    remainder = 0
    while n >= 64:
        remainder = remainder | (n & 1)
        n = n // 2
    return n + remainder


def node_power(start, left_size, right_size, total):
    # Dung hai lan trung diem de khong phai tinh so thuc.
    left = 2 * start + left_size
    right = left + left_size + right_size
    power = 0

    while True:
        power += 1
        if left >= total:
            left -= total
            right -= total
        elif right >= total:
            return power
        left *= 2
        right *= 2


def _reverse(a, start, end):
    left = start
    right = end - 1
    while left < right:
        a[left], a[right] = a[right], a[left]
        left += 1
        right -= 1


def _count_run(a, start, end):
    next_index = start + 1
    if next_index == end:
        return 1

    descending = a[next_index] < a[start]
    next_index += 1
    if descending:
        while next_index < end:
            if not a[next_index] < a[next_index - 1]:
                break
            next_index += 1
        # Chi dao run giam nghiem ngat, tranh dao thu tu cac khoa bang nhau.
        _reverse(a, start, next_index)
    else:
        while next_index < end:
            if a[next_index] < a[next_index - 1]:
                break
            next_index += 1
    return next_index - start


def _binary_insertion(a, start, end, sorted_end):
    for index in range(sorted_end, end):
        value = a[index]
        left = start
        right = index
        while left < right:
            middle = (left + right) // 2
            if value < a[middle]:
                right = middle
            else:
                left = middle + 1

        position = index
        while position > left:
            a[position] = a[position - 1]
            position -= 1
        a[left] = value


def _merge(a, start, middle, end):
    left_size = middle - start
    right_size = end - middle

    if left_size <= right_size:
        buffer = a[start:middle]
        left = 0
        right = middle
        destination = start
        while left < left_size and right < end:
            if a[right] < buffer[left]:
                a[destination] = a[right]
                right += 1
            else:
                a[destination] = buffer[left]
                left += 1
            destination += 1
        while left < left_size:
            a[destination] = buffer[left]
            left += 1
            destination += 1
    else:
        buffer = a[middle:end]
        left = middle - 1
        right = right_size - 1
        destination = end - 1
        while left >= start and right >= 0:
            if buffer[right] < a[left]:
                a[destination] = a[left]
                left -= 1
            else:
                # Gop tu cuoi: khoa bang nhau thi lay ben phai truoc.
                a[destination] = buffer[right]
                right -= 1
            destination -= 1
        while right >= 0:
            a[destination] = buffer[right]
            right -= 1
            destination -= 1


def _merge_at(a, stack, index, merge_function):
    start = stack[index][0]
    left_size = stack[index][1]
    right_size = stack[index + 1][1]
    merge_function(a, start, start + left_size, start + left_size + right_size)
    stack[index][1] = left_size + right_size
    del stack[index + 1]


def _push_run(a, stack, start, size, total, merge_function):
    if len(stack) > 0:
        previous = stack[-1]
        power = node_power(previous[0], previous[1], size, total)
        while len(stack) > 1 and stack[-2][2] > power:
            _merge_at(a, stack, len(stack) - 2, merge_function)
        stack[-1][2] = power
    # Moi phan tu luu vi tri bat dau, do dai va power.
    stack.append([start, size, 0])


def _finish_merges(a, stack, merge_function):
    while len(stack) > 1:
        index = len(stack) - 2
        if index > 0 and stack[index - 1][1] < stack[index + 1][1]:
            index -= 1
        _merge_at(a, stack, index, merge_function)


def _sort(a, use_natural_runs):
    n = len(a)
    if n < 2:
        return

    minrun = minrun_length(n)
    stack = []
    start = 0
    while start < n:
        if use_natural_runs:
            size = _count_run(a, start, n)
        else:
            size = 1

        required = min(minrun, n - start)
        if size < required:
            _binary_insertion(a, start, start + required, start + size)
            size = required

        _push_run(a, stack, start, size, n, _merge)
        start += size
    _finish_merges(a, stack, _merge)


def sort(a):
    _sort(a, True)


def sort_noa(a):
    # Khong nhan dien run. Moi khoi minrun deu duoc binary insertion sort.
    _sort(a, False)


def _count_run_counted(a, start, end, counts):
    next_index = start + 1
    if next_index == end:
        return 1

    counts["key_comparisons"] += 1
    descending = a[next_index] < a[start]
    next_index += 1
    if descending:
        while next_index < end:
            counts["key_comparisons"] += 1
            if not a[next_index] < a[next_index - 1]:
                break
            next_index += 1
        _reverse(a, start, next_index)
    else:
        while next_index < end:
            counts["key_comparisons"] += 1
            if a[next_index] < a[next_index - 1]:
                break
            next_index += 1
    return next_index - start


def _binary_insertion_counted(a, start, end, sorted_end, counts):
    for index in range(sorted_end, end):
        value = a[index]
        left = start
        right = index
        while left < right:
            middle = (left + right) // 2
            counts["key_comparisons"] += 1
            if value < a[middle]:
                right = middle
            else:
                left = middle + 1

        position = index
        while position > left:
            a[position] = a[position - 1]
            position -= 1
        a[left] = value


def _merge_counted(a, start, middle, end, counts):
    left_size = middle - start
    right_size = end - middle

    if left_size <= right_size:
        buffer = a[start:middle]
        left = 0
        right = middle
        destination = start
        while left < left_size and right < end:
            counts["key_comparisons"] += 1
            if a[right] < buffer[left]:
                a[destination] = a[right]
                right += 1
            else:
                a[destination] = buffer[left]
                left += 1
            destination += 1
        while left < left_size:
            a[destination] = buffer[left]
            left += 1
            destination += 1
    else:
        buffer = a[middle:end]
        left = middle - 1
        right = right_size - 1
        destination = end - 1
        while left >= start and right >= 0:
            counts["key_comparisons"] += 1
            if buffer[right] < a[left]:
                a[destination] = a[left]
                left -= 1
            else:
                a[destination] = buffer[right]
                right -= 1
            destination -= 1
        while right >= 0:
            a[destination] = buffer[right]
            right -= 1
            destination -= 1


def _sort_counted(a, use_natural_runs):
    counts = {
        "key_comparisons": 0,
        "array_reads": None,
        "array_writes": None,
        "run_count": None,
        "avg_run_len": None,
    }
    n = len(a)
    natural_count = 0
    natural_total = 0
    if use_natural_runs:
        counts["run_count"] = 0
        counts["avg_run_len"] = 0.0
        if n == 1:
            counts["run_count"] = 1
            counts["avg_run_len"] = 1.0
    if n < 2:
        return counts

    # Chi duong counted moi tao ham truyen bo dem vao merge.
    def merge_with_counts(values, start, middle, end):
        _merge_counted(values, start, middle, end, counts)

    minrun = minrun_length(n)
    stack = []
    start = 0
    while start < n:
        if use_natural_runs:
            size = _count_run_counted(a, start, n, counts)
            natural_count += 1
            natural_total += size
        else:
            size = 1

        required = min(minrun, n - start)
        if size < required:
            _binary_insertion_counted(a, start, start + required, start + size, counts)
            size = required

        _push_run(a, stack, start, size, n, merge_with_counts)
        start += size
    _finish_merges(a, stack, merge_with_counts)

    if use_natural_runs:
        counts["run_count"] = natural_count
        counts["avg_run_len"] = natural_total / natural_count
    return counts


def sort_counted(a):
    return _sort_counted(a, True)


def sort_noa_counted(a):
    return _sort_counted(a, False)
