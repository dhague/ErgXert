from enum import unique, Enum


@unique
class FileType(Enum):
    ERG=1
    MRC=2
    RPE=3

    @staticmethod
    def from_filename(filename: str):
        if filename.lower().endswith(".erg"):
            file_type = FileType.ERG
        elif filename.lower().endswith(".mrc"):
            file_type = FileType.MRC
        elif filename.lower().endswith(".rpe"):
            file_type = FileType.RPE
        else:
            raise TypeError("ERG/MRC files must end with .erg. or .mrc")
        return file_type