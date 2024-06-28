from typing import Dict
from traceq import analyzer
from .config import load_config
from .context import context


__all__ = ["compare_profiles"]


def compare_profiles(sessions: Dict, unit: str, output_dir: str) -> None:
    config = {
        "output_dir": output_dir,
        "analyzer": {
            "sessions": sessions,
            "unit": unit,
        },
    }
    load_config(config)

    analyzer.compare_profiles(context.config)
