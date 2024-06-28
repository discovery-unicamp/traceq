import sys

from typing import Optional, Callable
from pathlib import Path
from traceq.common.logger import logger


__all__ = ["execute_file"]


def execute_file(
    filepath: Path,
    args: tuple,
    kwargs: dict,
    function_name: Optional[str] = None,
    before: Callable = lambda: None,
    after: Callable = lambda: None,
) -> None:
    logger.info(
        f'Starting new profiler session for file "{filepath}" with entrypoint set to: "{function_name if function_name else "__main__"}"'
    )
    logger.debug(f"Using args: {args}")
    logger.debug(f"Using kwargs: {kwargs}")

    original_argv = sys.argv.copy()
    sys.argv = [str(filepath)] + list(args)
    exec_globals = {
        "__name__": "__main__.sub" if function_name else "__main__",
        "__file__": str(filepath),
        "__package__": None,
        "__builtins__": __builtins__,
    }

    with open(filepath, "r") as f:
        file_content = f.read()

    try:
        logger.info(f"Executing file: {filepath}")
        if function_name:
            logger.debug(f'Using function "{function_name}" as entrypoint')

        logger.info("Compiling code")
        compiled_code = compile(file_content, str(filepath), "exec")

        logger.info("Running execution before hook")
        before()

        logger.info("Executing code file")
        exec(compiled_code, exec_globals)
        function = exec_globals.get(function_name)
        if function:
            logger.info(f"Running function: {function_name}")
            function(*args, **kwargs)

        logger.info("Running execution after hook")
        after()
    finally:
        sys.argv = original_argv
        logger.info(f'File "{filepath}" finished execution')
