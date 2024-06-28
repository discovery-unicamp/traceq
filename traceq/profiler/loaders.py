import os
import msgpack
import gzip

from .types import Profile


__all__ = ["load_profile"]


def load_profile(filepath: str) -> Profile:
    with gzip.GzipFile(filepath, mode="rb") as gzip_file:
        return msgpack.unpackb(gzip_file.read(), raw=False)
