import uuid
import importlib
import inspect
import importlib.util

from pydantic import BaseModel, FilePath, field_validator, model_validator
from typing import Optional, Literal, List, Any
from enum import Enum


__all__ = [
    "ProfilerConfig",
    "Metric",
    "MemoryUsageBackend",
    "FunctionParameter",
]


class Metric(Enum):
    MEMORY_USAGE = "MEMORY_USAGE"
    TIME = "TIME"


class MemoryUsageBackend(Enum):
    PSUTIL = "PSUTIL"
    RESOURCE = "RESOURCE"
    TRACEMALLOC = "TRACEMALLOC"
    KERNEL = "KERNEL"


class MemoryUsageConfig(BaseModel):
    enabled_backends: List[MemoryUsageBackend] = [MemoryUsageBackend.KERNEL]

    @field_validator("enabled_backends", mode="before")
    def uppercase_enabled_backends(cls, v: Any) -> List[MemoryUsageBackend]:
        if isinstance(v, list):
            return [
                MemoryUsageBackend(i.upper()) if isinstance(i, str) else i for i in v
            ]

        return v


class FunctionParameter(BaseModel):
    name: str
    type: str
    position: int
    default: str = None


class ProfilerConfig(BaseModel):
    session_id: str = str(uuid.uuid4())
    enabled_metrics: List[Metric] = [Metric.MEMORY_USAGE, Metric.TIME]
    memory_usage: MemoryUsageConfig
    filepath: Optional[FilePath] = None
    entrypoint: Optional[str] = None
    signature: Optional[List[FunctionParameter]] = None
    args: tuple = tuple()
    kwargs: dict = {}
    depth: int = 3
    precision: float = 2
    sign_traces: bool = False
    strategy: Literal["thread", "process"] = "process"

    @field_validator("sign_traces", mode="before")
    def transform_is_trace_enabled(cls, v: Any) -> bool:
        if isinstance(v, bool):
            return v

        return v.lower() == "true"

    @field_validator("depth", mode="before")
    def transform_depth_to_int(cls, v: Any) -> int:
        if isinstance(v, int):
            return v

        return int(v)

    @field_validator("precision", mode="before")
    def transform_precision_to_float(cls, v: Any) -> float:
        if isinstance(v, float):
            return v

        precision = int(v)
        return float(1 * 10**-precision)

    @field_validator("enabled_metrics", mode="before")
    def uppercase_enabled_transports(cls, v: Any) -> List[Metric]:
        if isinstance(v, list):
            return [Metric(i.upper()) if isinstance(i, str) else i for i in v]

        return v

    @field_validator("kwargs", mode="before")
    def parse_kwargs(cls, v: Any):
        if isinstance(v, dict):
            return v
        if isinstance(v, list):
            result = {}
            for item in v:
                if "=" in item:
                    key, value = item.split("=", 1)
                    result[key] = value
                else:
                    raise ValueError(f"Invalid format for kwarg: {item}")
            return result

        raise TypeError("kwarg must be a list of strings or a dict")

    @field_validator("entrypoint")
    def check_function_exists(cls, v: Any, values):
        if v is None:
            return v
        filepath = values.data.get("filepath")
        if filepath is None:
            raise ValueError("File path must be set before checking function")

        spec = importlib.util.spec_from_file_location("module.name", filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if not hasattr(module, v):
            raise ValueError(f"Function '{v}' not found in {filepath}")
        return v

    @field_validator("signature", mode="before")
    def inject_signature(cls, v: Any, values):
        if v is not None:
            return v

        filepath = values.data.get("filepath")
        entrypoint = values.data.get("entrypoint")
        if filepath is None or entrypoint is None:
            return None

        spec = importlib.util.spec_from_file_location("module.name", filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        function = getattr(module, entrypoint)
        signature = inspect.signature(function)

        parameters = []
        position = 0
        for name, param in signature.parameters.items():
            param_type = (
                str(param.annotation.__name__)
                if param.annotation is not inspect.Parameter.empty
                else "Any"
            )
            default = (
                param.default if param.default is not inspect.Parameter.empty else None
            )
            parameters.append(
                {
                    "name": name,
                    "type": param_type,
                    "position": position,
                    "default": repr(default),
                }
            )

            position += 1

        return [FunctionParameter(**p) for p in parameters]

    @model_validator(mode="after")
    def define_strategy(cls, values):
        threaded_backends = [
            MemoryUsageBackend.RESOURCE,
            MemoryUsageBackend.TRACEMALLOC,
        ]
        if any(
            backend in values.memory_usage.enabled_backends
            for backend in threaded_backends
        ):
            values.strategy = "thread"

        return values
