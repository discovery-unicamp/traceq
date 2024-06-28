from typing import List, Dict, Optional
from toolz import curry
from enum import Enum


__all__ = [
    "unique",
    "deep_merge",
    "filter_defined_values",
    "str_as_list",
    "readable_enum_list",
    "from_key_value_string",
    "convert_to_unit",
]


def unique(values: List) -> List:
    unique_values = []
    for value in values:
        if value not in unique_values:
            unique_values.append(value)

    return unique_values


@curry
def deep_merge(old_dict: dict, new_dict: dict, append: bool = True) -> dict:
    merged = dict(old_dict)

    for key, value in new_dict.items():
        if key in old_dict and isinstance(value, dict):
            merged[key] = deep_merge(old_dict[key], value, append=append)
        elif key in old_dict and isinstance(value, list) and append:
            merged[key] = old_dict[key] + value
        elif value and value != "":
            merged[key] = value

    return merged


def filter_defined_values(data: dict, allow_empty_lists: bool = True) -> dict:
    if not isinstance(data, dict):
        return data

    filtered_data = {}
    for key, value in data.items():
        if isinstance(value, dict):
            nested = filter_defined_values(value, allow_empty_lists=allow_empty_lists)
            if nested:
                filtered_data[key] = nested
        elif isinstance(value, list):
            if len(value) > 0 or allow_empty_lists:
                filtered_data[key] = value
        elif value is not None:
            filtered_data[key] = value

    return filtered_data


def str_as_list(value: Optional[str], sep: str = ",") -> list:
    if not value:
        return []
    return [part for part in value.split(sep) if part and part != ""]


def readable_enum_list(enum_list: List[Enum]) -> str:
    return [enum.value for enum in enum_list]


def from_key_value_string(key_value_string: Optional[str], sep: str = "=") -> Dict:
    if not key_value_string:
        return {}

    return {
        key: value
        for key, value in [part.split(sep) for part in key_value_string.split(",")]
    }


def convert_to_unit(unit_to: str, unit_from: str, value: float) -> float:
    normalized_unit_to = unit_to.lower()
    normalized_unit_from = unit_from.lower()

    if normalized_unit_to == normalized_unit_from:
        return value

    conversion = {
        "b_to_b": 1,
        "b_to_kb": 1024,
        "b_to_mb": 1024**2,
        "b_to_gb": 1024**3,
        "kb_to_b": 1 / 1024,
        "kb_to_kb": 1,
        "kb_to_mb": 1024,
        "kb_to_gb": 1024**2,
        "mb_to_b": 1 / 1024**2,
        "mb_to_kb": 1 / 1024,
        "mb_to_mb": 1,
        "mb_to_gb": 1024,
        "gb_to_b": 1 / 1024**3,
        "gb_to_kb": 1 / 1024**2,
        "gb_to_mb": 1 / 1024,
        "gb_to_gb": 1,
        "s_to_ms": 1 / 1000,
        "ms_to_s": 1000,
        "s_to_s": 1,
    }

    conversion_key = f"{normalized_unit_from}_to_{normalized_unit_to}"
    if conversion_key not in conversion:
        raise ValueError(f"Conversion from {unit_from} to {unit_to} is not supported")

    return float(value / conversion[conversion_key])
