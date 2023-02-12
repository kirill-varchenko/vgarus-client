from pathlib import Path

import pytest

import vgarus_client.utils


@pytest.mark.parametrize(
    "raw_date,complited_date",
    [
        ("2023-04-21", "2023-04-21"),
        ("2023-04", "2023-04-01"),
        ("2023", "2023-01-01"),
    ],
)
def test_complete_iso_date_string(raw_date, complited_date):
    res = vgarus_client.utils.complete_iso_date_string(raw_date)
    assert res == complited_date


@pytest.mark.parametrize(
    "second_last_suffix,last_suffix,path,result",
    [
        ("result", "tsv", Path("test"), Path("test.result.tsv")),
        ("result", "tsv", Path("test.txt"), Path("test.result.tsv")),
        ("result", "tsv", Path("test.result.tsv"), Path("test.result.1.tsv")),
        ("result", "tsv", Path("test.result.1.tsv"), Path("test.result.2.tsv")),
    ],
)
def test_iter_enumerated_suffix(second_last_suffix, last_suffix, path, result):
    res = next(
        vgarus_client.utils.iter_enumerated_suffix(
            path, second_last_suffix, last_suffix
        )
    )
    assert res == result
