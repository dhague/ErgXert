from html.parser import HTMLParser
import json
import os
import requests

XERT_URL = "https://www.xertonline.com"
USERNAME = os.environ['XERT_USERNAME']
PASSWORD = os.environ['XERT_PASSWORD']
TP  = os.environ['XERT_TP']  # e.g. 230
HIE = os.environ['XERT_HIE'] # e.g. 19800
PP  = os.environ['XERT_PP']  # e.g. 858

SSL_VERIFY = True

FILE_TYPE = os.environ['XERT_FILE_TYPE']
FILE_NAME = os.environ['XERT_FILE_NAME']

# FILE_TYPE = "ERG"
# FILE_TYPE = "MRC"
# FILE_TYPE = "RPE"
# FILE_NAME = "data/DownwardSpiral_2015.erg"
# FILE_NAME = "data/DownwardSpiral_2015.mrc"
# FILE_NAME = "data/DownwardSpiral_2015.rpe"
# FILE_NAME = "data/HellHathNoFury_2013.mrc"


class XertWorkout:
    def __init__(self):
        self.name = ""
        self.rows = []


xert_workout = XertWorkout()

class Xert:
    def __init__(self):
        self.s = requests.Session()

    def login(self, username, password):
        class XertTokenHTMLParser(HTMLParser):
            def handle_starttag(self, tag, attrs):
                # Find an <input> tag with name="_token" and get the value as self.token
                if self.token==None and tag=="input":
                    token=False
                    for name, value in attrs:
                        if name == "name":
                            if value != "_token":
                                break;
                            else:
                                token=True
                                continue
                        if token and name=="value":
                            self.token = value

        r = self.s.get(XERT_URL, verify=SSL_VERIFY)
        token_parser = XertTokenHTMLParser()
        token_parser.token = None
        token_parser.feed(str(r.content))
        self.s.post(XERT_URL + "/auth/login",
                       {"_token": token_parser.token, "username": username, "password": password},
                       verify=SSL_VERIFY,
                       allow_redirects=False)


    def create_workout(self, workout: XertWorkout):
        w = self.s.post(XERT_URL + "/workout",
                   {"name": workout.name,
                    "description": "",
                    "rows": json.dumps(xert_workout.rows),
                    "pp" : str(PP),
                    "atc": str(HIE),
                    "ftp": str(TP),
                    "submit": "save"},
                   headers= {
                             "X-Requested-With": "XMLHttpRequest"
                             },
                   verify=SSL_VERIFY)
        return w.json()

xert = Xert()
xert.login(USERNAME, PASSWORD)

f = open(FILE_NAME, 'r')
lines = f.read().splitlines()

if FILE_TYPE == "ERG" or FILE_TYPE == "MRC":
    ftpMode = FILE_TYPE == "MRC"
    ftp = 100
    line = lines.pop(0)
    # Parse the header section
    while line != "[COURSE DATA]":
        if FILE_TYPE == "ERG" and line.startswith("FTP"):
            ftpMode = True
            ftp = int(line.split("=")[1].strip())
        if line.startswith("DESCRIPTION"):
            xert_workout.name = line.split("=")[1].strip()
        line = lines.pop(0)

    # Get the workout data
    workout_data = []
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
            print("Error: Xert workout steps cannot do power ramps, so pairs of lines must have identical power")
            print("First line power: " + line1[1] + ", second line power: " + line2[1])
            print("Skipping interval")
            continue;
        else:
            if ftpMode:
                value = int(100 * float(line1[1]) / ftp)
            else:
                value = int(line1[1])
        duration = float(line2[0]) - float(line1[0])
        mins = int(duration)
        secs = round((duration - mins) * 60)
        workout_data.append({"value": value, "mins": mins, "secs": secs, "type": xert_type})

if FILE_TYPE == "RPE":
    # TODO
    print("TODO")

rownum = 0
more_data = True
# Create a dict matching Xert's JSON structure for intervals
while more_data:
    row = {}
    row["sequence"] = rownum
    rownum = rownum + 1
    row["name"] = ""
    valid_row = False
    try:
        int_line = workout_data.pop(0)
        row["power"] = {"value": int_line["value"], "type": int_line["type"]}
        row["duration"] = {"value": str.format("{:02}:{:02}", int_line["mins"], int_line["secs"]), "type": "absolute"}
        valid_row = True
        int_line = workout_data.pop(0)
        row["rib_power"] = {"value": int_line["value"], "type": int_line["type"]}
        row["rib_duration"] = {"value": str.format("{:02}:{:02}", int_line["mins"], int_line["secs"]), "type": "absolute"}
    except IndexError:
        if valid_row:
            row["rib_power"] = {"value": 0, "type": "absolute"}
            row["rib_duration"] = {"value": "00:00", "type": "absolute"}
        more_data = False
    if valid_row:
        row["interval_count"] = "1"
        xert_workout.rows.append(row)

print("Processed workout " + xert_workout.name + " - now creating in Xert...")

result = xert.create_workout(xert_workout)

print("Created workout - URL is "+result["redirect"])
