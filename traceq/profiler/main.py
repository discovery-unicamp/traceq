import random

from traceq.config import Config
from traceq.common.logger import logger
from traceq.common.synchronization import run_subprocess
from .handlers import execute_file
from .tracer import Tracer
from .builders import build_trace_hooks, build_profile, build_metadata


__all__ = ["run_profiler"]


def run_profiler(config: Config) -> None:
    logger.info("Starting profiler")

    trace_hooks = build_trace_hooks(
        config.profiler.enabled_metrics,
        config.profiler.memory_usage.enabled_backends,
    )
    tracer = Tracer(
        trace_hooks,
        config.profiler.precision,
        config.profiler.sign_traces,
        config.profiler.strategy,
        config.profiler.depth,
    )

    target_args = (
        config.profiler.filepath,
        config.profiler.args,
        config.profiler.kwargs,
    )
    target_kwargs = {
        "function_name": config.profiler.entrypoint,
        **tracer.executor_hooks,
    }

    logger.debug(f"Using config: {config}")
    logger.debug(f"Enabled trace hooks: {trace_hooks.keys()}")
    logger.debug(f"Enabled metrics: {config.profiler.enabled_metrics}")
    logger.debug(f"Using args: {config.profiler.args}")
    logger.debug(f"Using kwargs: {config.profiler.kwargs}")
    logger.debug(f"Using entrypoint: {config.profiler.entrypoint}")

    logger.info(f'Starting profiler execution for "{config.profiler.filepath}"')

    run_subprocess(execute_file, sync=True, *target_args, **target_kwargs)

    logger.info("Profiler execution finished")
    logger.debug(f"Amount of captured traces: {len(tracer)}")
    logger.info("Saving profile data")

    metadata = build_metadata(
        signature=config.profiler.signature,
        args=config.profiler.args,
        kwargs=config.profiler.kwargs,
    )
    logger.debug(f"Using metadata: {metadata}")

    profile_filepath = f"{config.output_dir}/{config.profiler.session_id}.prof"
    trace_list = tracer.build_trace_list()
    logger.debug(f"Sample captured trace: {random.choice(trace_list)}")
    build_profile(metadata, trace_list, profile_filepath)

    logger.info(f"Profiler output saved to: {config.output_dir}")
