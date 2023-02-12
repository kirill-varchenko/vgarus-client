import itertools
import re
from pathlib import Path
from typing import Generator, Iterable, TypeVar


def complete_iso_date_string(s: str) -> str:
    # 2023-04-21 -> 2023-04-21
    # 2023-04    -> 2023-04-01
    # 2023       -> 2023-01-01
    return "-".join((components := s.split("-")) + ["01"] * (3 - len(components)))


def normalize_name(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "_", name)


T = TypeVar("T")


def iter_batches(data: Iterable[T], size: int) -> Generator[list[T], None, None]:
    """Batch data into lists of length n. The last batch may be shorter."""

    if size < 1:
        raise ValueError("n must be at least one")
    it = iter(data)
    while batch := list(itertools.islice(it, size)):
        yield batch


def iter_enumerated_suffix(
    start_path: Path, second_last_suffix: str, last_suffix: str
) -> Generator[Path, None, None]:
    """Generated enumerated suffixes from path"""

    path = start_path
    while True:
        if len(path.suffixes) < 2:
            path = path.with_suffix(f".{second_last_suffix}.{last_suffix}")
        else:
            suffix2 = path.suffixes[-2].removeprefix(".")
            if suffix2 == second_last_suffix:
                path = path.with_suffix(f".1.{last_suffix}")
            elif suffix2.isdigit():
                path = path.with_suffix("")
                new_counter = int(suffix2) + 1
                path = path.with_suffix(f".{new_counter}.{last_suffix}")
        yield path
