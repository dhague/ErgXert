from html.parser import HTMLParser
import json
import os
from typing import List

import requests

from erg_xert.workout import WorkoutStep


class Xert:
    URL = "https://www.xertonline.com"
    # Use some plausible defaults if signature values aren't defined
    TP = os.environ.get('XERT_TP', 250)
    HIE = os.environ.get('XERT_HIE', 20000)
    PP = os.environ.get('XERT_PP', 1000)

    class Workout:
        def __init__(self):
            self.name = ""
            self.rows = []

    def __init__(self):
        self.s = requests.Session()
        self.ssl_verify = True

    def login(self, username, password):
        class XertTokenHTMLParser(HTMLParser):
            def handle_starttag(self, tag, attrs):
                # Find an <input> tag with name="_token" and get the value as self.token
                if self.token == None and tag == "input":
                    token = False
                    for name, value in attrs:
                        if name == "name":
                            if value != "_token":
                                break;
                            else:
                                token = True
                                continue
                        if token and name == "value":
                            self.token = value

        r = self.s.get(Xert.URL, verify=self.ssl_verify)
        token_parser = XertTokenHTMLParser()
        token_parser.token = None
        token_parser.feed(str(r.content))
        self.s.post(Xert.URL + "/auth/login",
                    {"_token": token_parser.token, "username": username, "password": password},
                    verify=self.ssl_verify,
                    allow_redirects=False)


    def workout_from_steps(self, workout_name, workout_data: List[WorkoutStep]):
        # Create a dict matching Xert's JSON structure for intervals
        rownum = 0
        workout = Xert.Workout()
        workout.name = workout_name

        while workout_data:
            row = {}
            row["sequence"] = rownum
            rownum = rownum + 1
            row["name"] = ""
            valid_row = False
            try:
                step = workout_data.pop(0)
                row["power"] = {"value": step.value, "type": step.type}
                row["duration"] = {"value": str.format("{:02}:{:02}", step.mins, step.secs), "type": "absolute"}
                valid_row = True
                step = workout_data.pop(0)
                row["rib_power"] = {"value": step.value, "type": step.type}
                row["rib_duration"] = {"value": str.format("{:02}:{:02}", step.mins, step.secs),
                                       "type": "absolute"}
            except IndexError:
                if valid_row:
                    row["rib_power"] = {"value": 0, "type": "absolute"}
                    row["rib_duration"] = {"value": "00:00", "type": "absolute"}
            if valid_row:
                row["interval_count"] = "1"
                workout.rows.append(row)
        return workout


    def create_workout(self, workout: Workout):
        w = self.s.post(Xert.URL + "/workout",
                        {"name": workout.name,
                         "description": "",
                         "rows": json.dumps(workout.rows),
                         "pp": str(Xert.PP),
                         "atc": str(Xert.HIE),
                         "ftp": str(Xert.TP),
                         "submit": "save"},
                        headers={
                            "X-Requested-With": "XMLHttpRequest"
                        },
                        verify=self.ssl_verify)
        return w.json()

