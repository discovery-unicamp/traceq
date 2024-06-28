from io import TextIOWrapper
from toolz import curry


__all__ = ["go_to_pointer", "get_line_with_keyword"]


@curry
def go_to_pointer(pointer: int, file: TextIOWrapper) -> TextIOWrapper:
    file.seek(pointer)
    return file


@curry
def get_line_with_keyword(keyword: str, file: TextIOWrapper) -> str:
    for line in file:
        if keyword in line:
            return line

    return ""
