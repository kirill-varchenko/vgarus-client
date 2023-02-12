import csv
import json
import logging
import logging.config
import math
from pathlib import Path

import click
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

import vgarus_client.client
import vgarus_client.logging_config
import vgarus_client.models
import vgarus_client.readers
import vgarus_client.service
import vgarus_client.utils

logging.config.dictConfig(vgarus_client.logging_config.LOGGING)
logger = logging.getLogger("vgarus")


@click.group()
def cli():
    pass


@cli.command()
@click.argument("package", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--basename", "-b", help="Basename for output files")
def split_package(package: Path, basename: str | None = None) -> None:
    """Split single json package to fasta and metadata tsv"""

    p = vgarus_client.models.Package.parse_file(package)

    metadata = p.to_tsv()
    fasta = p.to_fasta()

    base = Path(basename) if basename else package
    with open(base.with_suffix(".tsv"), "w") as fo:
        fo.write(metadata)
    with open(base.with_suffix(".fasta"), "w") as fo:
        fo.write(fasta)


@cli.command()
@click.option(
    "--metadata", "-m", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option(
    "--fasta", "-f", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option("--basename", "-b", help="Basename for output file")
def combine_package(metadata: Path, fasta: Path, basename: str | None = None) -> None:
    """Combine metadata tsv and fasta to a single json package"""

    p = vgarus_client.readers.read_fasta_and_tsv_to_package(
        fasta_file=fasta, tsv_file=metadata
    )

    base = Path(basename) if basename else metadata

    with open(base.with_suffix(".json"), "w") as fo:
        fo.write(p.to_json())


@cli.command()
@click.option("--native/--no-native", help="Field names as in VGARus", default=False)
def metadata_template(native: bool) -> None:
    """Prints tsv header for metadata"""

    if not native:
        print(*vgarus_client.models.SampleData.__fields__.keys(), sep="\t")
    else:
        print(
            *[
                field.alias if field.alias else field_name
                for field_name, field in vgarus_client.models.SampleData.__fields__.items()
            ],
            sep="\t"
        )


@cli.command()
@click.option("--username", "-u")
@click.option("--password", "-p")
@click.option(
    "--env",
    "-e",
    type=click.Path(dir_okay=False, path_type=Path),
    default=Path("~/.vgarus.env"),
    show_default=True,
)
def dictionaries(username: str | None, password: str | None, env: Path | None) -> None:
    """Get VGARUS dictionaries"""

    client = vgarus_client.service.get_client(
        username=username, password=password, env=env
    )
    if client is None:
        click.echo("Pass username and password or env file")
        return

    dicts = client.get_dictionary()
    click.echo(json.dumps(dicts, ensure_ascii=False, indent=2))


@cli.command()
@click.option(
    "--package", "-j", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option(
    "--metadata", "-m", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option(
    "--fasta", "-f", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option("--username", "-u")
@click.option("--password", "-p")
@click.option(
    "--env",
    "-e",
    type=click.Path(dir_okay=False, path_type=Path),
    default=Path("~/.vgarus.env"),
    show_default=True,
)
@click.option("--batch-size", "-s", type=int, default=1, show_default=True)
@click.option("--basename", "-b", help="Basename for outputs")
def upload(
    package: Path | None,
    metadata: Path | None,
    fasta: Path | None,
    username: str | None,
    password: str | None,
    env: Path | None,
    batch_size: int = 1,
    basename: str | None = None,
) -> None:
    """Upload to VGARUS"""

    if package is not None and metadata is None and fasta is None:
        p = vgarus_client.models.Package.parse_file(package)
        base = Path(basename) if basename else package
    elif package is None and metadata is not None and fasta is not None:
        p = vgarus_client.readers.read_fasta_and_tsv_to_package(
            fasta_file=fasta, tsv_file=metadata
        )
        base = Path(basename) if basename else metadata
    else:
        click.echo("Specify package or metadata with fasta")
        return

    client = vgarus_client.service.get_client(
        username=username, password=password, env=env
    )
    if client is None:
        click.echo("Pass username and password or env file")
        return

    results_path = base
    for path in vgarus_client.utils.iter_enumerated_suffix(
        base, second_last_suffix="result", last_suffix="tsv"
    ):
        results_path = path
        if not path.exists():
            break

    leftover_path = base
    for path in vgarus_client.utils.iter_enumerated_suffix(
        base, second_last_suffix="leftover", last_suffix="tsv"
    ):
        leftover_path = path
        if not path.exists():
            break

    batch_number = math.ceil(len(p) / batch_size)

    ok, not_ok = 0, 0
    with tqdm(
        desc="Uploading", total=batch_number
    ) as progress, logging_redirect_tqdm(), open(results_path, "w") as results_o, open(
        leftover_path, "w"
    ) as leftover_o:
        results_writer = csv.DictWriter(
            results_o,
            fieldnames=vgarus_client.models.UploadResult.__fields__.keys(),
            delimiter="\t",
        )
        leftover_writer = csv.DictWriter(
            leftover_o,
            fieldnames=vgarus_client.models.SampleData.__fields__.keys(),
            delimiter="\t",
        )
        results_writer.writeheader()
        leftover_writer.writeheader()

        for result, batch in vgarus_client.service.upload_package(
            client, package=p, batch_size=batch_size
        ):
            for upload_result, sample in zip(result, batch):
                if upload_result.ok:
                    ok += 1
                    results_writer.writerow(upload_result.dict())
                else:
                    not_ok += 1
                    leftover_writer.writerow(sample.sample_data.dict())

            progress.set_postfix(ok=ok, not_ok=not_ok)
            progress.update()

    if not_ok == 0:
        leftover_path.unlink()


if __name__ == "__main__":
    cli()
