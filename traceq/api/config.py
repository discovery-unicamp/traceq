from traceq.config import Config
from traceq.common.transformers import deep_merge
from traceq.common.logger import setup_logger_from_config
from .context import context


__all__ = ["load_config"]


def load_config(config: dict) -> None:
    old_config = context.config.model_dump()
    new_config = deep_merge(old_config, config, append=False)

    context.config = Config(**new_config)

    if "logger" in config:
        setup_logger_from_config(context.config)
