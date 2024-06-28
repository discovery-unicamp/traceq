from pydantic import BaseModel, field_validator
from typing import Any, Dict, Literal
from enum import Enum


__all__ = ["AnalyzerConfig", "MemoryUsageUnit", "Sessions"]


class MemoryUsageUnit(Enum):
    B = "b"
    KB = "kb"
    MB = "mb"
    GB = "gb"


Sessions = Dict[str, str]


class AnalyzerConfig(BaseModel):
    sessions: Sessions = {}
    unit: MemoryUsageUnit = MemoryUsageUnit.MB

    @field_validator("unit", mode="before")
    def uppercase_enabled_backends(cls, v: Any) -> MemoryUsageUnit:
        if isinstance(v, str):
            return MemoryUsageUnit(v.lower())

        return v
