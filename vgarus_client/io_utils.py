import csv
import io
import logging
from pathlib import Path
from typing import Generator

import pyfastx
from pydantic import parse_file_as

from . import models

logger = logging.getLogger("vgarus")


def iter_fasta(fasta_file: Path) -> Generator[models.Sequence, None, None]:
    fa = pyfastx.Fastx(str(fasta_file))
    for name, seq in fa:
        yield models.Sequence(header=name, body=seq)


def iter_sample_data(tsv_file: Path) -> Generator[models.SampleData, None, None]:
    with open(tsv_file, "r") as fi:
        reader = csv.DictReader(fi, delimiter="\t")
        for row in reader:
            yield models.SampleData.parse_obj(row)


def read_json_to_samples(json_file: Path) -> list[models.Sample]:
    return parse_file_as(list[models.Sample], json_file)


def read_fasta_and_tsv_to_samples(
    fasta_file: Path, tsv_file: Path
) -> list[models.Sample]:
    sequences = {sequence.header: sequence for sequence in iter_fasta(fasta_file)}
    samples: list[models.Sample] = []
    for data in iter_sample_data(tsv_file):
        if data.virus_name not in sequences:
            logger.warning(
                "Virus name from metadata not found in fasta: %s", data.virus_name
            )
            continue
        samples.append(
            models.Sample.construct(
                sample_data=data, sequence=sequences[data.virus_name]
            )
        )
    return samples


def samples_to_tsv(samples: list[models.Sample]) -> str:
    with io.StringIO() as buffer:
        writer = csv.DictWriter(
            buffer, fieldnames=models.SampleData.__fields__.keys(), delimiter="\t"
        )
        writer.writeheader()
        writer.writerows(sample.sample_data.dict() for sample in samples)
        return buffer.getvalue()


def samples_to_fasta(samples: list[models.Sample]) -> str:
    return "\n".join(sample.sequence.to_fasta() for sample in samples)

