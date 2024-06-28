import time

from traceq.common.transformers import convert_to_unit
from traceq.profiler.types import CapturedTrace
from .types import TimeUnit


__all__ = ["on_sample"]


def get_unix_timestamp(unit: TimeUnit = "ms") -> float:
    unix_timestamp = time.perf_counter()
    return convert_to_unit(unit, "s", unix_timestamp)


def capture_trace() -> CapturedTrace:
    unix_timestamp = get_unix_timestamp()

    return "unix_timestamp", int(unix_timestamp)


on_sample = capture_trace
