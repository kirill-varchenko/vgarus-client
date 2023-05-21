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
