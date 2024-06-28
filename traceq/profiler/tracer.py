import sys
import time
import random
import re

from multiprocessing import shared_memory, Manager, Process
from threading import Thread, Event
from typing import Any, Optional, List
from types import FrameType
from traceq.common.logger import logger
from traceq.common.synchronization import do_many, run_subprocess, run_thread
from .types import (
    ExecutorHooks,
    TraceFunction,
    TraceHooks,
    SignedCapturedTrace,
    TraceList,
    Strategy,
)


__all__ = ["Tracer"]


class Tracer:
    captured_traces: List[SignedCapturedTrace]

    __sign_traces: bool
    __current_depth: int = 0
    __max_depth: int = 3
    __strategy: Strategy
    __precision: float
    __trace_hooks: TraceHooks
    __shm: shared_memory.SharedMemory
    __shm_size: int = 100
    __default_signature: str = "unknown::unknown:0::unknown"
    __sampler_thread: Optional[Thread] = None
    __sampler_process: Optional[Process] = None
    __sampler_finished: Event
    __strategy_handlers = {
        "thread": run_thread,
        "process": run_subprocess,
    }

    def __init__(
        self,
        trace_hooks: TraceHooks,
        precision: float,
        sign_traces: bool,
        strategy: Strategy,
        max_depth: int,
    ) -> None:
        self.__sign_traces = sign_traces
        self.__precision = precision
        self.__trace_hooks = trace_hooks
        self.__strategy = strategy
        self.__max_depth = max_depth

        self.__shm = shared_memory.SharedMemory(create=True, size=self.__shm_size)
        self.set_signature(self.__default_signature)
        self.set_sync_objects()

    @property
    def executor_hooks(self) -> ExecutorHooks:
        logger.debug(f"Using executor hooks: {self.__trace_hooks}")

        return {
            "before": self.before_executor,
            "after": self.after_executor,
        }

    @property
    def signature(self) -> str:
        return bytes(self.__shm.buf[: self.__shm_size]).rstrip(b" ").decode("utf-8")

    def build_trace_list(self) -> TraceList:
        return [
            {"signature": trace[0], **{key: value for key, value in trace[1]}}
            for trace in self.captured_traces
        ]

    def before_executor(self) -> None:
        logger.debug("Running before executor hooks")

        do_many(self.__trace_hooks.get("before", []))

        if self.__sign_traces:
            self.start_tracer()

        self.start_sampler()

    def after_executor(self) -> None:
        logger.debug("Running after executor hooks")

        do_many(self.__trace_hooks.get("after", []))

        if self.__sign_traces:
            self.stop_tracer()

        self.stop_sampler()
        self.close_shm()

    def start_tracer(self) -> None:
        logger.info("Starting profile tracer")
        count = 0

        def tracer(frame: FrameType, event: str, _: Any) -> Optional[TraceFunction]:
            if "c_" in event:
                return None

            self.new_event(event)
            if self.__current_depth >= self.__max_depth:
                return None

            module_name = frame.f_globals.get("__name__", frame.f_code.co_filename)
            function = frame.f_code.co_name
            source = f"{module_name}:{frame.f_code.co_firstlineno}"
            signature = f"{event}::{source}::{function}"
            self.set_signature(signature)

            return tracer

        sys.setprofile(tracer)

    def new_event(self, event: str) -> None:
        if event == "call":
            self.__current_depth += 1
        elif event == "return":
            self.__current_depth -= 1

    def stop_tracer(self) -> None:
        sys.setprofile(None)
        logger.info("Profile tracer stopped")

    def close_shm(self) -> None:
        self.__shm.close()
        self.__shm.unlink()

    def set_signature(self, signature: str) -> None:
        self.__shm.buf[: self.__shm_size] = signature.ljust(
            self.__shm_size,
            " ",
        ).encode("utf-8")

    def set_sync_objects(self) -> None:
        manager = Manager()
        self.__sampler_finished = manager.Event()
        self.captured_traces = manager.list()

    def start_sampler(self) -> None:
        logger.info("Starting profile sampler")
        logger.info(
            f"Using precision of {self.__precision}s and {self.__strategy} strategy"
        )

        hooks = self.__trace_hooks.get("on_sample", [])
        strategy_handler = self.__strategy_handlers.get(self.__strategy)
        self.__sampler_thread = strategy_handler(self.sampler, *hooks)

    def stop_sampler(self) -> None:
        self.__sampler_finished.set()

        if self.__sampler_thread:
            self.__sampler_thread.join()

        if self.__sampler_process:
            self.__sampler_process.join()

        logger.info("Profile sampler stopped")

    def sampler(self, *hooks: List[TraceFunction]) -> None:
        while not self.__sampler_finished.is_set():
            event = self.signature
            captured_traces = do_many(hooks)
            self.captured_traces.append((event, captured_traces))

            time.sleep(self.__precision)

    def get_random_trace(self) -> SignedCapturedTrace:
        return random.choice(self.captured_traces)

    def __len__(self) -> int:
        return len(self.captured_traces)
