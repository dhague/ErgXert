import os

from erg_xert.erg_mrc import ErgMrcFile
from erg_xert.xert import Xert

USERNAME = os.environ['XERT_USERNAME']
PASSWORD = os.environ['XERT_PASSWORD']

FILE_TYPE = os.environ['XERT_FILE_TYPE']
FILE_NAME = os.environ['XERT_FILE_NAME']

# Example values:
# FILE_TYPE = "ERG"
# FILE_TYPE = "MRC"
# FILE_TYPE = "RPE"
# FILE_NAME = "data/DownwardSpiral_2015.erg"
# FILE_NAME = "data/DownwardSpiral_2015.mrc"
# FILE_NAME = "data/DownwardSpiral_2015.rpe"
# FILE_NAME = "data/HellHathNoFury_2013.mrc"

if ErgMrcFile.is_erg_mrc_file(FILE_NAME):
    workout_name, workout_data = ErgMrcFile.load_from_file(FILE_NAME)

# TODO - RPE file format
# if RpeFile.is_rpe_file(FILE_NAME):
#     workout_name, workout_data = RpeFile.load_from_file(FILE_NAME)

xert = Xert()
workout = xert.workout_from_steps(workout_name, workout_data)

print("Loaded workout " + workout.name + " - now creating in Xert...")

xert.login(USERNAME, PASSWORD)
result = xert.create_workout(workout)

print("Created workout - URL is " + result["redirect"])
