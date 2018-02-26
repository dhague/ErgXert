class WorkoutStep:
    def __init__(self, value: int, mins: int, secs: int, type: str, description: str = ""):
        self.value = value
        self.mins = mins
        self.secs = secs
        self.type = type
        self.description = description
