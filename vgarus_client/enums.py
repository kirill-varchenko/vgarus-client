from enum import IntEnum


class Specimen(IntEnum):
    SWAB = 0
    FECES = 1
    AUTOPSYMATERIAL = 2
    OTHER = 3


class Passage(IntEnum):
    ORIGINAL = 1
    CULTURE = 2


class SeqTechnology(IntEnum):
    ILLUMINA = 0
    ION_TORRENT = 1
    BGI = 2
    OXFORD_NANOPORE = 3
    PACBIO = 4
    SANGER = 5
    OTHER = 6


class Target(IntEnum):
    WHOLEGENOME = 1
    FRAGMENT = 2


class PatientGender(IntEnum):
    UNKNOWN = 0
    MALE = 1
    FEMALE = 2


class LungDamage(IntEnum):
    UNKNOWN = 0
    CT1 = 1
    CT2 = 2
    CT3 = 3
    CT4 = 4
    NO = 5


class Vaccine(IntEnum):
    NO = 0
    SPUTNIKV = 1
    EPIVACCORONA = 2
    COVIVAC = 3
    OTHER = 4


class Outcome(IntEnum):
    UNKNOWN = 0
    RECOVERY = 1
    ILL = 2
    DECEASE = 3


class Travel(IntEnum):
    NO = 0
    ABROAD = 1
    DOMESTIC = 2


class Reinfection(IntEnum):
    NO = 0
    YES = 1
