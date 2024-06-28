import os
import sys

from loguru import logger
from toolz import compose, do, curry
from traceq.config import Config, LoggerTransport
from .builders import isonow


__all__ = ["logger", "setup_logger_from_config"]


def clear_handlers(_: Config) -> None:
    logger.remove()


def set_transports(config: Config) -> None:
    available_transports = {
        LoggerTransport.CONSOLE: set_console_transport,
        LoggerTransport.FILE: set_file_transport,
    }

    for transport in config.logger.enabled_transports:
        transport_handler = available_transports.get(transport)
        if not transport_handler:
            raise ValueError(f'Invalid logger handler: "{transport}"')

        transport_handler(config)


def set_console_transport(config: Config) -> None:
    logger.add(sys.stdout, level=config.logger.level.value)


def set_file_transport(config: Config) -> None:
    now = isonow()
    filename = f"{now}.log"
    filepath = os.path.join(config.output_dir, filename)
    logger.add(filepath, level=config.logger.level.value)


setup_logger_from_config = compose(
    curry(do)(set_transports),
    curry(do)(clear_handlers),
)
