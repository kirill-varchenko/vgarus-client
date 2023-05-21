import logging
import math
from pathlib import Path
from typing import Generator

from vgarus_client import client, models, utils

logger = logging.getLogger("vgarus")


def get_client(
    username: str | None, password: str | None, env: Path | None
) -> client.VgarusClient | None:
    try:
        if username and password:
            vgarus_auth = models.VgarusAuth(username=username, password=password)
        elif env and env.expanduser().exists():
            vgarus_auth = models.VgarusAuth(_env_file=env)  # type: ignore
        else:
            vgarus_auth = models.VgarusAuth()  # type: ignore
    except:
        logger.exception("No credentials")
        return None

    return client.VgarusClient(auth=vgarus_auth)


def get_upload_results(
    batch: list[models.Sample], response: models.VgarusResponse
) -> list[models.UploadResult]:
    results = [
        models.UploadResult(
            virus_name=sample.sample_data.virus_name,
            gisaid_id=sample.sample_data.gisaid_id,
        )
        for sample in batch
    ]

    if response.status != 200:
        return results

    virus_names_in_errors = response.get_errors_virus_names()

    i = 0
    for upload_result in results:
        if upload_result.virus_name in virus_names_in_errors:
            continue
        upload_result.vgarus_id = response.message[i]
        i += 1

    return results


def upload_samples(
    client: client.VgarusClient,
    samples: list[models.Sample],
    batch_size: int = 1,
) -> Generator[tuple[list[models.UploadResult], list[models.Sample]], None, None,]:
    """Handles batched upload and gathering results"""

    batch_number = math.ceil(len(samples) / batch_size)
    logger.info(
        "Uploading %s records in %s batches by %s",
        len(samples),
        batch_number,
        batch_size,
    )

    for batch in utils.iter_batches(samples, batch_size):
        vgarus_response = client.send_batch(batch)
        logger.debug("%s", vgarus_response.json())

        if vgarus_response.status == 200:
            result = get_upload_results(batch, vgarus_response)

            yield result, batch
        else:
            yield [], []
