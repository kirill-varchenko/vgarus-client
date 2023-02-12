import logging
import math
from pathlib import Path
from typing import Generator

import vgarus_client.client
import vgarus_client.models
import vgarus_client.utils

logger = logging.getLogger("vgarus")


def get_client(
    username: str | None, password: str | None, env: Path | None
) -> vgarus_client.client.VgarusClient | None:
    try:
        if username and password:
            vgarus_auth = vgarus_client.models.VgarusAuth(
                username=username, password=password
            )
        elif env and env.expanduser().exists():
            vgarus_auth = vgarus_client.models.VgarusAuth(_env_file=env)  # type: ignore
        else:
            vgarus_auth = vgarus_client.models.VgarusAuth()  # type: ignore
    except:
        logger.exception("No credentials")
        return None

    return vgarus_client.client.VgarusClient(auth=vgarus_auth)


def upload_package(
    client: vgarus_client.client.VgarusClient,
    package: vgarus_client.models.Package,
    batch_size: int = 1,
) -> Generator[
    tuple[list[vgarus_client.models.UploadResult], list[vgarus_client.models.Sample]],
    None,
    None,
]:
    """Handles batched upload and gathering results"""

    batch_number = math.ceil(len(package) / batch_size)
    logger.info(
        "Uploading %s records in %s batches by %s",
        len(package),
        batch_number,
        batch_size,
    )

    for batch in vgarus_client.utils.iter_batches(package, batch_size):
        data = [sample.dict(by_alias=True, exclude_none=True) for sample in batch]
        raw_results = client.send_data(data)
        if len(raw_results) == len(batch):
            result = [
                vgarus_client.models.UploadResult(
                    virus_name=sample.sample_data.virus_name,
                    gisaid_id=sample.sample_data.gisaid_id,
                    vgarus_id=raw_result,
                )
                for sample, raw_result in zip(batch, raw_results)
            ]
        else:
            logger.warning(
                "Send result lenth mismatch: %s, batch size: %s",
                len(raw_results),
                len(batch),
            )
            result = [
                vgarus_client.models.UploadResult(
                    virus_name=sample.sample_data.virus_name,
                    gisaid_id=sample.sample_data.gisaid_id,
                    vgarus_id=None,
                )
                for sample in batch
            ]

        yield result, batch
