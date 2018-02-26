from enum import unique, Enum


@unique
class FileType(Enum):
    ERG=1
    MRC=2
    RPE=3
