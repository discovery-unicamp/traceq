import pandas as pd


__all__ = ["build_metadata_annotation"]


def build_metadata_annotation(df: pd.DataFrame) -> str:
    entrypoint_metadata = [
        (key.replace("entrypoint_", ""), value)
        for key, value in df.attrs.items()
        if key.startswith("entrypoint_")
    ]
    metadata_str = ", ".join(f"{key}={value}" for key, value in entrypoint_metadata)

    return metadata_str
