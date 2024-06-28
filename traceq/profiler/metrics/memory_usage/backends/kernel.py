from traceq.common.file_handling import get_line_with_keyword, go_to_pointer
from traceq.profiler.types import CapturedTrace


__all__ = ["before", "on_sample"]


status_file = open("/proc/self/status", "r")


def get_memory_usage() -> float:
    file_content = go_to_pointer(0, status_file)
    status_line = get_line_with_keyword("VmRSS", file_content)
    memory_usage = status_line.split(":")[1].split()[0]

    return float(memory_usage)


def capture_trace() -> CapturedTrace:
    memory_usage = get_memory_usage()
    return "kernel_memory_usage", memory_usage


def before() -> None:
    globals()["status_file"] = open("/proc/self/status", "r")


on_sample = capture_trace
