import pandas as pd

from typing import List, Literal
from toolz import curry
from traceq.common.transformers import convert_to_unit
from traceq.common.logger import logger
from traceq.profiler.loaders import load_profile


__all__ = [
    "to_unit",
    "to_memory_usage_evolution",
    "profile_to_dataframe",
]


def to_memory_usage_evolution(
    profile: pd.DataFrame,
    memory_usage_column: Literal[
        "kernel_memory_usage",
        "psutil_memory_usage",
        "resource_memory_usage",
        "tracemalloc_memory_usage",
    ],
    columns_to_keep: List[str] = [
        "value",
        "unit",
        "unix_timestamp",
        "signature",
    ],
) -> pd.DataFrame:
    memory_usage_profile = profile.copy()

    if memory_usage_column not in profile.columns:
        raise ValueError(f"The column {memory_usage_column} is not in the DataFrame.")

    memory_usage_profile["value"] = pd.to_numeric(
        profile[memory_usage_column], errors="coerce"
    )

    unit = profile.attrs.get(f"{memory_usage_column}_unit")
    if unit is None:
        raise ValueError(
            f"No unit metadata found for {memory_usage_column}. Please ensure it has a unit attribute."
        )

    memory_usage_profile["unit"] = unit

    columns_to_drop = set(memory_usage_profile.columns) - set(columns_to_keep)

    return memory_usage_profile.drop(columns=columns_to_drop)


@curry
def column_to_unit(column_name: str, unit: str, profile: pd.DataFrame) -> pd.DataFrame:
    current_unit = profile.attrs.get(f"{column_name}_unit")

    if current_unit is None:
        raise ValueError(
            f"No unit metadata found for {column_name}. Please ensure it has a unit attribute."
        )

    profile[column_name] = profile[column_name].apply(
        lambda x: convert_to_unit(unit, current_unit, x)
    )

    profile.attrs[f"{column_name}_unit"] = unit

    return profile


def profile_to_dataframe(file_path: str) -> pd.DataFrame:
    logger.debug(f"Loading profile data from {file_path} as DataFrame")

    profile_data = load_profile(file_path)
    metadata = profile_data.get("metadata", {})
    trace_data = profile_data.get("data", [])

    logger.debug(f"Using metadata: {metadata}")

    df = pd.DataFrame(trace_data)
    for key, value in metadata.items():
        df.attrs[key] = value

    return df
