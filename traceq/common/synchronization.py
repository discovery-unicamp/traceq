from typing import Callable, List, Any
from functools import wraps
from multiprocessing import Process
from threading import Thread
from .logger import logger


__all__ = ["lazy", "passthrough", "run_subprocess", "run_thread", "do_many"]


def lazy(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        @wraps(func)
        def delayed():
            return func(*args, **kwargs)

        return delayed

    return wrapper


def passthrough(*args, **kwargs):
    return args, kwargs


def run_subprocess(
    target: Callable,
    *target_args,
    sync: bool = False,
    **target_kwargs,
) -> Process:
    process = Process(target=target, args=target_args, kwargs=target_kwargs)

    process.start()

    if sync:
        process.join()

    return process


def run_thread(
    target: Callable,
    *target_args,
    sync: bool = False,
    **target_kwargs,
) -> Thread:
    thread = Thread(target=target, args=target_args, kwargs=target_kwargs)

    thread.start()

    if sync:
        thread.join()

    return thread


def do_many(fns: List[Callable], *args, **kwargs) -> List[Any]:
    results = []

    for fn in fns:
        try:
            result = fn(*args, **kwargs)
            results.append(result)
        except Exception as e:
            logger.error(f"Error executing function: {e}")

    return results
