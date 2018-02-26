import logging
from datetime import timedelta
from typing import List

from erg_xert.file_type import FileType
from erg_xert.workout import WorkoutStep


class RpeFile:
    logger = logging.getLogger('RpeFile')

    @staticmethod
    def is_rpe_file(filename: str):
        try:
            file_type = FileType.from_filename(filename)
        except TypeError:
            return False

        return file_type == FileType.RPE

    @staticmethod
    def load_rpe_mappings(filename: str = "rpeMappings.ini"):
        with open(filename, 'r') as f:
            lines = f.read().splitlines()

        line = lines.pop(0)
        # Go past the comments & empty lines
        while line.startswith("#") or len(line.strip())==0:
            line = lines.pop(0)

        # The current line is now the first line of actual data, so push it back into the list
        lines.insert(0, line)

        rpe_mapping = {}
        allowable_types = ["absolute", "relative_ftp", "relative_ltp", "relative_pp", "hmmp", "xssr"]
        while lines:
            line = lines.pop(0)
            rpe_val = line.split("=")
            rpe = float(rpe_val[0].strip())
            num_type = rpe_val[1].split()
            num = float(num_type[0])
            type = num_type[1]
            if type not in allowable_types:
                raise TypeError("XertType "+type+" is not in the allowable list of "+str(allowable_types))
            rpe_mapping[rpe] = (num, type)

        return rpe_mapping

    @staticmethod
    def load_from_file(filename: str, rpe_map: dict):
        logger = RpeFile.logger

        with open(filename, 'r') as f:
            lines = f.read().splitlines()

        line = lines.pop(0)
        # Parse the header section
        while line.startswith("#") or len(line.strip())==0:
            if line.strip("#").strip().startswith("DESCRIPTION"):
                workout_name = line.split("=")[1].strip()
            line = lines.pop(0)

        # The current line is now the first line of actual data, so push it back into the list
        lines.insert(0, line)

        # Process the workout data
        workout_data: List[WorkoutStep] = []


        while lines:
            line1 = lines.pop(0)
            # Empty line means the end of the file
            if line1.strip() == "":
                break;
            line2 = lines.pop(0)
            line1 = line1.split("\t")
            line2 = line2.split("\t")
            rpe1 = float(line1[3])
            rpe2 = float(line2[3])
            if rpe1 != rpe2:
                logger.error(
                    "Error: Xert workout steps cannot do power ramps, so pairs of lines must have identical RPE")
                logger.error("First line RPE: " + rpe1 + ", second line RPE: " + rpe2)
                logger.error("Skipping interval")
                continue;
            try:
                xert_num, xert_type = rpe_map[rpe1]
            except KeyError:
                logger.error("Error: Couldn't fine RPE mapping for RPE value "+str(rpe1))
                logger.error("Skipping interval")
                continue;

            time1_fields = line1[1].split(":")
            time1 = timedelta(hours=int(time1_fields[0]),
                              minutes=int(time1_fields[1]),
                              seconds=int(time1_fields[2]))
            time2_fields = line2[1].split(":")
            time2 = timedelta(hours=int(time2_fields[0]),
                              minutes=int(time2_fields[1]),
                              seconds=int(time2_fields[2]))
            duration = time2 - time1
            mins = int(duration.total_seconds()/60)
            secs = int(duration.total_seconds()) % 60
            description = line1[0]
            workout_data.append(WorkoutStep(xert_num, mins, secs, xert_type, description))
        return workout_name, workout_data
