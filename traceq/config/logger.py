from typing import List, Any
from enum import Enum
from pydantic import BaseModel, field_validator


__all__ = ["LoggerConfig", "Transport"]


class Transport(Enum):
    CONSOLE = "CONSOLE"
    FILE = "FILE"


class Level(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LoggerConfig(BaseModel):
    enabled_transports: List[Transport] = [Transport.CONSOLE]
    level: Level = Level.INFO

    @field_validator("enabled_transports", mode="before")
    def uppercase_enabled_transports(cls, v: Any) -> List[Transport]:
        if isinstance(v, list):
            return [Transport(i.upper()) if isinstance(i, str) else i for i in v]

        return v

    @field_validator("level", mode="before")
    def uppercase_level(cls, v: Any) -> Level:
        if isinstance(v, str):
            v = v.upper()

        return Level(v)
