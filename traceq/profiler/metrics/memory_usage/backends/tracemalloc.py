import tracemalloc

from traceq.profiler.types import CapturedTrace


__all__ = ["before", "on_sample", "after"]


def get_memory_usage() -> float:
    memory_usage = tracemalloc.get_traced_memory()[0]

    return float(memory_usage)


def capture_trace() -> CapturedTrace:
    memory_usage = get_memory_usage()
    return "tracemalloc_memory_usage", memory_usage


before = tracemalloc.start
after = tracemalloc.stop
on_sample = capture_trace
