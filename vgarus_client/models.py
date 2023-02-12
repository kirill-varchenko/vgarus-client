from __future__ import annotations

import csv
import io
import re
from datetime import date

from pydantic import (BaseModel, BaseSettings, Field, NonNegativeInt,
                      root_validator, validator)

from . import enums, utils


class SampleData(BaseModel):
    virus_name: str = Field(alias="sample_name")
    collection_date: str = Field(alias="sample_pick_date")
    location: str = Field(alias="sample_pick_place")
    authors: str = Field(alias="author")
    gisaid_id: str

    specimen: enums.Specimen = Field(alias="biomater")
    passage: enums.Passage = Field(alias="sample_type")
    seq_technology: enums.SeqTechnology | None = Field(alias="tech")
    assembly_method: str | None = Field(alias="genom_pick_method")
    target: enums.Target = Field(alias="seq_area")

    patient_age: NonNegativeInt | None
    patient_gender: enums.PatientGender | None
    lung_damage: enums.LungDamage
    vaccine: enums.Vaccine
    outcome: enums.Outcome = Field(alias="issue")
    travel: enums.Travel = Field(alias="foreign")
    reinfection: enums.Reinfection = Field(alias="double_sick")

    class Config:
        allow_population_by_field_name = True
        use_enum_values = True

    _normalize_sample_name = validator("virus_name", allow_reuse=True, pre=True)(
        utils.normalize_name
    )

    @validator(
        "patient_age", "patient_gender", "seq_technology", "assembly_method", pre=True
    )
    def replace_empty_strings_with_none(cls, v: str):
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

    @validator("collection_date")
    def validate_iso_date(cls, v: str) -> str:
        compete_raw_date = utils.complete_iso_date_string(v)
        date.fromisoformat(compete_raw_date)  # Will raise ValueError for a wrong date
        return v


# TODO Something is wrong with this model
class Fasta(BaseModel):
    __root__: str

    @root_validator
    def clean_fasta(cls, values):
        s = re.search(
            r"^>(?P<title>.*?)$\s*(?P<sequence>[^>]*)", values["__root__"], re.MULTILINE
        )
        if not s:
            raise ValueError("Incorrect fasta")
        title = utils.normalize_name(s.group("title").strip())
        sequence = re.sub(r"\s", "", s.group("sequence"))
        if not sequence:
            raise ValueError("Empty sequence")
        return {"__root__": f">{title}\n{sequence}"}

    @property
    def title(self) -> str:
        return self.__root__.partition("\n")[0].removeprefix(">")

    def __eq__(self, other) -> bool:
        return self.__root__ == other


class Sample(BaseModel):
    sample_data: SampleData
    sequence: Fasta

    @root_validator
    def names_match(cls, values):
        if values["sample_data"].virus_name != values["sequence"].title:
            raise ValueError("Sample data virus name and sequence title mismach")
        return values


class Package(BaseModel):
    __root__: list[Sample]

    def __iter__(self):
        return iter(self.__root__)

    def __getitem__(self, idx) -> Sample:
        return self.__root__[idx]

    def __len__(self) -> int:
        return len(self.__root__)

    def to_json(self) -> str:
        return self.json(exclude_none=True, by_alias=True, ensure_ascii=False, indent=2)

    def to_fasta(self) -> str:
        return "\n".join(sample.sequence.__root__ for sample in self.__root__)

    def to_tsv(self) -> str:
        with io.StringIO() as buffer:
            writer = csv.DictWriter(
                buffer, fieldnames=SampleData.__fields__.keys(), delimiter="\t"
            )
            writer.writeheader()
            writer.writerows(sample.sample_data.dict() for sample in self.__root__)
            return buffer.getvalue()


class VgarusAuth(BaseSettings):
    username: str
    password: str

    class Config:
        env_prefix = "VGARUS_"
        case_sensitive = False


class UploadResult(BaseModel):
    virus_name: str
    gisaid_id: str
    submittion_date: date = Field(default_factory=date.today)
    vgarus_id: str | None

    @property
    def ok(self) -> bool:
        return self.vgarus_id is not None
