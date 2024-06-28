from toolz import compose, curry, do
from traceq.config import Config
from traceq.common.logger import setup_logger_from_config


__all__ = ["context"]


class Context:
    config: Config = compose(
        curry(do)(setup_logger_from_config),
        Config.from_initial_config,
    )()


context = Context()
