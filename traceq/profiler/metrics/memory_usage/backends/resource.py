import resource

from traceq.profiler.types import CapturedTrace


__all__ = ["on_sample"]


def get_memory_usage() -> float:
    memory_usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    return float(memory_usage)


def capture_trace() -> CapturedTrace:
    memory_usage = get_memory_usage()
    return "resource_memory_usage", memory_usage


on_sample = capture_trace
