from typing import Callable, TypedDict, List, Any, Tuple, Optional, Literal, Dict


__all__ = [
    "TraceFunction",
    "TraceHooks",
    "TraceList",
    "Trace",
    "CapturedTrace",
    "SignedCapturedTrace",
    "ExecutorHooks",
    "Profile",
    "Strategy",
]

Strategy = Literal["thread", "process"]
TraceKey = str
Signature = str
CapturedTrace = Tuple[TraceKey, Any]
SignedCapturedTrace = Tuple[Signature, CapturedTrace]
TraceFunction = Callable[[], CapturedTrace]


class Trace(TypedDict):
    signature: Signature
    kernel_memory_usage: Optional[float]
    psutil_memory_usage: Optional[float]
    resource_memory_usage: Optional[float]
    tracemalloc_memory_usage: Optional[float]
    unix_timestamp: Optional[int]


TraceList = List[Trace]


class Profile(TypedDict):
    metadata: Dict
    data: TraceList


class TraceHooks(TypedDict):
    before: List[TraceFunction]
    on_sample: List[TraceFunction]
    after: List[TraceFunction]


class ExecutorHooks(TypedDict):
    before: Callable
    after: Callable
