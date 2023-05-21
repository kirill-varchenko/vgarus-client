import warnings

import pytest
from hypothesis import strategies as st
from hypothesis.errors import NonInteractiveExampleWarning

import vgarus_client.models
import vgarus_client.service


@pytest.mark.parametrize(
    "virus_names,response,vgarus_ids",
    [
        (
            ["virus1, virus2, virus3"],
            vgarus_client.models.VgarusResponse(
                status=200, message=["id1", "id2", "id3"]
            ),
            ["id1", "id2", "id3"],
        ),
        (
            ["virus1, virus2, virus3"],
            vgarus_client.models.VgarusResponse(
                status=200, message=["id1", "id3"], errors=["sample_name: virus2"]
            ),
            ["id1", None, "id3"],
        ),
        (
            ["virus1, virus2, virus3"],
            vgarus_client.models.VgarusResponse(
                status=200, message=["id1", "id2"], errors=["sample_name: virus3"]
            ),
            ["id1", "id2", None],
        ),
        (
            ["virus1, virus2, virus3"],
            vgarus_client.models.VgarusResponse(status=500, message=[]),
            [None, None, None],
        ),
        (
            ["virus1, virus2, virus3"],
            vgarus_client.models.VgarusResponse(
                status=500, message=["id1", "id2", "id3"]
            ),
            [None, None, None],
        ),
    ],
)
def test_get_upload_results(virus_names, response, vgarus_ids):
    batch = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=NonInteractiveExampleWarning)
        for virus_name in virus_names:
            sample_data = st.builds(
                vgarus_client.models.SampleData,
                sample_name=st.just(virus_name),
                sample_pick_date=st.just("2023-05-21"),
            ).example()
            sample = vgarus_client.models.Sample(
                sample_data=sample_data,
                sequence=vgarus_client.models.Sequence(header=virus_name, body=""),
            )
            batch.append(sample)

    results = vgarus_client.service.get_upload_results(batch, response)

    assert len(results) == len(batch)
    for result, vgarus_id in zip(results, vgarus_ids):
        assert result.vgarus_id == vgarus_id
