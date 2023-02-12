import csv
import logging
from pathlib import Path
from typing import Generator

import pyfastx
from pydantic import parse_file_as

from . import models

logger = logging.getLogger("vgarus")


def iter_fasta(fasta_file: Path) -> Generator[models.Fasta, None, None]:
    fa = pyfastx.Fastx(fasta_file)
    for name, seq in fa:
        yield models.Fasta(__root__=f">{name}\n{seq}")


def iter_sample_data(tsv_file: Path) -> Generator[models.SampleData, None, None]:
    with open(tsv_file, "r") as fi:
        reader = csv.DictReader(fi, delimiter="\t")
        for row in reader:
            yield models.SampleData.parse_obj(row)


def read_json_to_package(json_file: Path) -> models.Package:
    return parse_file_as(models.Package, json_file)


def read_fasta_and_tsv_to_package(fasta_file: Path, tsv_file: Path) -> models.Package:
    fastas = {fasta.title: fasta for fasta in iter_fasta(fasta_file)}
    samples = []
    for data in iter_sample_data(tsv_file):
        if data.virus_name not in fastas:
            logger.warning(
                "Virus name from metadata not found in fasta: %s", data.virus_name
            )
            continue
        samples.append(
            models.Sample.construct(sample_data=data, sequence=fastas[data.virus_name])
        )
    return models.Package(__root__=samples)
