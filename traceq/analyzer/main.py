from toolz import compose
from traceq.common.logger import logger
from traceq.config import Config
from .transformers import (
    column_to_unit,
    to_memory_usage_evolution,
    profile_to_dataframe,
)
from .plotters import plot_memory_usage_comparison, plot_execution_time_comparison


__all__ = ["compare_profiles"]


def compare_profiles(config: Config) -> None:
    logger.info("Starting profiles comparison")
    logger.debug(f"Using config: {config}")

    parse_profile = compose(
        *(
            column_to_unit(column, config.analyzer.unit.value)
            for column in [
                "kernel_memory_usage",
                "psutil_memory_usage",
                "resource_memory_usage",
                "tracemalloc_memory_usage",
            ]
        ),
        profile_to_dataframe,
    )

    logger.info("Parsing collected profiles")
    collected_profiles = {
        name: parse_profile(path) for name, path in config.analyzer.sessions.items()
    }

    logger.debug("Parsing memory usage evolution data")

    memory_usage_evolution = {
        backend: to_memory_usage_evolution(profile, f"{backend}_memory_usage")
        for backend, profile in collected_profiles.items()
    }

    plot_memory_usage_comparison(memory_usage_evolution, config.output_dir)
    plot_execution_time_comparison(memory_usage_evolution, config.output_dir)

    logger.info(f"Finished profiles comparison. Results saved to {config.output_dir}")
