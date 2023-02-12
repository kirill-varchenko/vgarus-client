import pydantic.error_wrappers
import pytest

import vgarus_client.models


def test_fasta():
    fasta = vgarus_client.models.Fasta(__root__=">abc\ncde\nfgh\n\n")
    assert fasta == ">abc\ncdefgh"
    assert fasta.title == "abc"


@pytest.mark.parametrize(
    "incorrect_fasta",
    [
        ">abc\n",
        "abc\ncde\nfgh\n\n",
    ],
)
def test_fasta_exceptions(incorrect_fasta):
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        vgarus_client.models.Fasta(__root__=incorrect_fasta)
