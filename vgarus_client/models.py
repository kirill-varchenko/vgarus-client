from __future__ import annotations

import json
import re
from datetime import date

from pydantic import (
    BaseModel,
    BaseSettings,
    Field,
    NonNegativeInt,
    root_validator,
    validator,
)

from . import enums, utils

RE_VIRUS_NAME_IN_RESPONSE_ERRORS = re.compile(r"sample_name: (.*?):")


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

    @validator("collection_date", pre=True)
    def validate_iso_date(cls, v: str) -> str:
        complete_raw_date = utils.complete_iso_date_string(v)
        date.fromisoformat(complete_raw_date)  # Will raise ValueError for a wrong date
        return complete_raw_date


class Sequence(BaseModel):
    header: str
    body: str

    @validator("header")
    def normalize_header(cls, v):
        return utils.normalize_name(v)

    @validator("body")
    def remove_whitespaces(cls, v):
        return utils.remove_whitespaces(v)

    @classmethod
    def parse_fasta(cls, fasta: str) -> Sequence:
        s = re.search(r"^>(?P<header>.*?)$\s*(?P<body>[^>]*)", fasta, re.MULTILINE)
        if not s:
            raise ValueError("Incorrect fasta")
        return cls(**s.groupdict())

    def __eq__(self, other: Sequence) -> bool:
        return self.header == other.header

    def to_fasta(self) -> str:
        return f">{self.header}\n{self.body}"

    def __repr__(self) -> str:
        return f"Sequence(header={self.header!r}, body='{self.body[:10]}...')"


class Sample(BaseModel):
    sample_data: SampleData
    sequence: Sequence

    @root_validator(pre=True)
    def parse_fasta(cls, values):
        if isinstance(values["sequence"], str):
            values["sequence"] = Sequence.parse_fasta(values["sequence"])
        return values

    @root_validator
    def names_match(cls, values):
        if values["sample_data"].virus_name != values["sequence"].header:
            raise ValueError("Sample data virus name and sequence header mismach")
        return values

    def export(self) -> dict:
        """Export Sample as a dict suitable for posting to VgaRus."""

        return {
            "sample_data": self.sample_data.dict(by_alias=True, exclude_none=True),
            "sequence": self.sequence.to_fasta(),
        }


class VgarusAuth(BaseSettings):
    username: str
    password: str

    class Config:
        env_prefix = "VGARUS_"
        case_sensitive = False


class VgarusResponse(BaseModel):
    status: int
    message: list[str]
    errors: list[str] = []

    @validator("errors", pre=True)
    def parse_errors(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v

    @validator("message", pre=True)
    def parse_input_json(cls, v):
        if isinstance(v, list):
            return v
        try:
            parsed = json.loads(v)
            return parsed.get("inputJson", [])
        except:
            pass
        return []

    def get_errors_virus_names(self) -> list[str]:
        return [
            s.group(1)
            for error in self.errors
            if (s := RE_VIRUS_NAME_IN_RESPONSE_ERRORS.search(error))
        ]


class UploadResult(BaseModel):
    virus_name: str
    gisaid_id: str
    submittion_date: date = Field(default_factory=date.today)
    vgarus_id: str | None = None

    @property
    def ok(self) -> bool:
        return self.vgarus_id is not None
