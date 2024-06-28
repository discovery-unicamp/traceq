from psutil import Process
from traceq.profiler.types import CapturedTrace


__all__ = ["before", "on_sample"]


process = Process()


def get_memory_usage() -> float:
    memory_usage = process.memory_info().rss

    return float(memory_usage)


def capture_trace() -> CapturedTrace:
    memory_usage = get_memory_usage()
    return "psutil_memory_usage", memory_usage


def before() -> None:
    globals()["process"] = Process()


on_sample = capture_trace
