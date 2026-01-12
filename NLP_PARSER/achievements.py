import re

KEYWORDS = ["winner", "rank", "award", "certified", "top"]

def extract_achievements(text: str) -> list:
    achievements = []

    for line in text.split("\n"):
        if any(k in line.lower() for k in KEYWORDS):
            achievements.append(line.strip())

    return achievements
