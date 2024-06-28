import msgpack
import gzip

from typing import List, Dict, Tuple
from traceq.config import MemoryUsageBackend, ProfilerMetric, FunctionParameter
from traceq.common.transformers import deep_merge
from traceq.common.logger import logger
from .metrics.memory_usage import build_trace_hooks as build_memory_usage_trace_hooks
from .metrics.time import build_trace_hooks as build_time_trace_hooks
from .types import TraceHooks, TraceList


__all__ = ["build_trace_hooks", "build_profile", "build_metadata"]


def build_trace_hooks(
    enabled_metrics: List[ProfilerMetric],
    enabled_memory_usage_backends: List[MemoryUsageBackend],
) -> TraceHooks:
    logger.debug(f"Building trace hooks for enabled metrics: {enabled_metrics}")

    memory_usage_hooks = (
        build_memory_usage_trace_hooks(enabled_memory_usage_backends)
        if ProfilerMetric.MEMORY_USAGE in enabled_metrics
        else {}
    )
    time_hooks = (
        build_time_trace_hooks() if ProfilerMetric.TIME in enabled_metrics else {}
    )
    return deep_merge(memory_usage_hooks, time_hooks, append=True)


def build_metadata(
    signature: List[FunctionParameter],
    args: Tuple,
    kwargs: Dict,
) -> Dict:
    entrypoint_args_names = [param.name for param in signature]
    entrypoint_args = {entrypoint_args_names[i]: str(arg) for i, arg in enumerate(args)}
    entrypoint_kwargs = {k: str(v) for k, v in kwargs.items()}

    return {
        **{
            f"entrypoint_{arg_name}": arg_value
            for arg_name, arg_value in entrypoint_args.items()
        },
        **{
            f"entrypoint_{arg_name}": arg_value
            for arg_name, arg_value in entrypoint_kwargs.items()
        },
        "kernel_memory_usage_unit": "kb",
        "psutil_memory_usage_unit": "b",
        "resource_memory_usage_unit": "kb",
        "tracemalloc_memory_usage_unit": "b",
        "unix_timestamp_unit": "ms",
    }


def build_profile(
    metadata: Dict,
    trace_list: TraceList,
    output_file: str,
) -> None:
    logger.debug("Building profile")

    data = build_profile_data(trace_list)

    profile = {
        "metadata": metadata,
        "data": data,
    }
    serialized_profile = msgpack.packb(profile, use_bin_type=True)

    with gzip.GzipFile(output_file, "wb") as gzip_file:
        gzip_file.write(serialized_profile)


def build_profile_data(trace_list: TraceList) -> list:
    default_value = {
        "signature": "UNKNOWN",
        "kernel_memory_usage": 0,
        "psutil_memory_usage": 0,
        "resource_memory_usage": 0,
        "tracemalloc_memory_usage": 0,
        "unix_timestamp": 0,
    }

    return [
        {key: trace.get(key, default_value[key]) for key in default_value}
        for trace in trace_list
    ]
