from argparse import ArgumentParser, _SubParsersAction, Namespace
from toolz import do, compose, curry
from .config import Config
from .common.cli import AppendUnique
from .common.logger import logger, setup_logger_from_config
from .profiler import attach_args as attach_profiler_args
from .analyzer import attach_args as attach_analyzer_args


__all__ = ["cli"]


def cli():
    namespace = parse_namespace()
    config = Config.from_namespace(namespace)
    setup_logger_from_config(config)

    logger.info("Initializing TraceQ execution")
    logger.debug(f"Namespace: {namespace}")
    logger.debug(f"Config: {config}")
    logger.debug(f'Running "{namespace.func.__name__}" command')

    namespace.func(config)


def build_parser() -> ArgumentParser:
    return ArgumentParser(
        description="TraceQ simplifies profiling and modeling the memory usage of Python programs"
    )


def attach_global_args(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--output-dir",
        "-o",
        help="Output directory to save the profiling results (default: ./)",
    )

    parser.add_argument(
        "--log-level",
        "-l",
        help="Logging level to use for the profiler (default: info)",
        choices=["debug", "info", "warning", "error", "critical"],
    )

    parser.add_argument(
        "--log-transport",
        help="Enable a specific log transport (default: console,file)",
        choices=["console", "file"],
        action=AppendUnique,
    )


def get_subparsers(parser: ArgumentParser) -> _SubParsersAction:
    return parser.add_subparsers()


def to_namespace(parser: ArgumentParser) -> Namespace:
    return parser.parse_args()


attach_subparsers = curry(do)(
    compose(
        attach_analyzer_args,
        attach_profiler_args,
        get_subparsers,
    )
)


attach_args = compose(
    attach_subparsers,
    curry(do)(attach_global_args),
)

parse_namespace = compose(
    to_namespace,
    attach_args,
    build_parser,
)


if __name__ == "__main__":
    cli()
