from traceq.profiler.types import TraceHooks
from .tracer import on_sample


__all__ = ["build_tracer"]


def build_trace_hooks() -> TraceHooks:
    return {
        "on_sample": [on_sample],
    }
