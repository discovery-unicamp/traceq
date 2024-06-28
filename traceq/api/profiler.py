import inspect

from typing import Callable
from traceq.profiler import run_profiler
from traceq.profiler.loaders import load_profile
from .config import load_config
from .context import context


__all__ = ["profile", "load_profile"]


def profile(function: Callable, *args, **kwargs) -> None:
    function_filepath = inspect.getfile(function)
    function_name = function.__name__

    config = {
        "profiler": {
            "filepath": function_filepath,
            "entrypoint": function_name,
            "args": args,
            "kwargs": kwargs,
        }
    }
    load_config(config)

    run_profiler(context.config)
