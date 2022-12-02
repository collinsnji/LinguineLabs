from dataclasses import dataclass


@dataclass
class Config:
    ROOT_DIR = ""
    THERAPY_WORDS = {
        "trauma": 0,
        "traumatic": 0,
        "traumatized": 0,
        "traumatizing": 0,
        "ptsd": 0,
        "depression": 0,
        "great depression": 0,
        "depressed": 0,
        "suicidal": 0,
        "depressing": 0,
        "anxiety": 0,
        "ocd": 0,
        "obsessive compulsive disorder": 0,
        "schizophrenia": 0,
        "bipolar": 0,
        "bipolar disorder": 0,
        "psychosis": 0,
        "psychotic": 0,
        "shell shock": 0
    }
