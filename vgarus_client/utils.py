import itertools
import re
from typing import Generator, Iterable, TypeVar

T = TypeVar("T")


def complete_iso_date_string(s: str) -> str:
    # 2023-04-21 -> 2023-04-21
    # 2023-04    -> 2023-04-01
    # 2023       -> 2023-01-01
    parts = s.split("-")
    year = parts[0]
    month = parts[1].zfill(2) if len(parts) > 1 and parts[1] else "01"
    day = parts[2].zfill(2) if len(parts) > 2 and parts[2] else "01"
    return f"{year}-{month}-{day}"


def normalize_name(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "_", name)


def remove_whitespaces(s: str) -> str:
    return re.sub(r"\s", "", s)


def iter_batches(data: Iterable[T], size: int) -> Generator[list[T], None, None]:
    """Batch data into lists of length n. The last batch may be shorter."""

    if size < 1:
        raise ValueError("n must be at least one")
    it = iter(data)
    while batch := list(itertools.islice(it, size)):
        yield batch
