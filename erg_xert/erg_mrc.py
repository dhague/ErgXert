import logging
from typing import List

from erg_xert.file_type import FileType
from erg_xert.workout import WorkoutStep


class ErgMrcFile:
    logger = logging.getLogger('ErgMrcFile')

    def is_erg_mrc_file(filename: str):
        return filename.lower().endswith(".erg") or filename.lower().endswith(".mrc")

    def load_from_file(filename: str):
        logger = ErgMrcFile.logger
        if filename.lower().endswith(".erg"):
            file_type = FileType.ERG
        elif filename.lower().endswith(".mrc"):
            file_type = FileType.MRC
        else:
            raise TypeError("ERG/MRC files must end with .erg. or .mrc")

        ftpMode = file_type == FileType.MRC
        ftp = 100
        with open(filename, 'r') as f:
            lines = f.read().splitlines()

        line = lines.pop(0)
        # Parse the header section
        while line != "[COURSE DATA]":
            if file_type == FileType.ERG and line.startswith("FTP"):
                ftpMode = True
                ftp = int(line.split("=")[1].strip())
            if line.startswith("DESCRIPTION"):
                workout_name = line.split("=")[1].strip()
            line = lines.pop(0)

        # Get the workout data from the COURSE DATA section
        workout_data: List[WorkoutStep] = []
        more_data = True

        if ftpMode:
            xert_type = "relative_ftp"
        else:
            xert_type = "absolute"

        while more_data:
            line1 = lines.pop(0)
            if line1 == "[END COURSE DATA]":
                more_data = False;
                continue;
            line2 = lines.pop(0)
            line1 = line1.split()
            line2 = line2.split()
            if line1[1] != line2[1]:
                logger.warning(
                    "Error: Xert workout steps cannot do power ramps, so pairs of lines must have identical power")
                logger.warning("First line power: " + line1[1] + ", second line power: " + line2[1])
                logger.warning("Skipping interval")
                continue;
            else:
                if ftpMode:
                    value = int(100 * float(line1[1]) / ftp)
                else:
                    value = int(line1[1])
            duration = float(line2[0]) - float(line1[0])
            mins = int(duration)
            secs = round((duration - mins) * 60)
            workout_data.append(WorkoutStep(value, mins, secs, xert_type))
        return workout_name, workout_data
