from datetime import datetime, timezone


__all__ = ["isonow", "timestamp"]


def isonow() -> str:
    return now().isoformat()


def timestamp() -> str:
    return now().timestamp()


def now() -> datetime:
    return datetime.now(timezone.utc)
