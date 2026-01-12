import re

ROLE_KEYWORDS = [
    "intern", "engineer", "developer",
    "analyst", "scientist", "architect"
]

EDUCATION_BLOCKLIST = [
    "college", "university", "institute",
    "bachelor", "b.e", "b.tech", "degree"
]

DATE_PATTERN = r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec).*?\d{4}|present'

def is_title_line(line: str) -> bool:
    if len(line) > 70:
        return False
    if "," in line and not line.isupper():
        return False
    return line.isupper() or line.istitle()

def looks_like_company(line: str) -> bool:
    lower = line.lower()
    if any(v in lower for v in ["working", "developed", "built", "using"]):
        return False
    if line.startswith("-"):
        return False
    return True

def extract_experience(text: str) -> list:
    experiences = []
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    current = None
    last_bullet_idx = None

    for line in lines:
        lower = line.lower()


        if any(e in lower for e in EDUCATION_BLOCKLIST):
            continue

    
        if any(r in lower for r in ROLE_KEYWORDS) and is_title_line(line):
            if current:
                experiences.append(current)

            current = {
                "company": "",
                "role": line,
                "duration": "",
                "responsibilities": []
            }
            last_bullet_idx = None
            continue

        if current and not current["company"] and looks_like_company(line):
            current["company"] = line.split("-")[0].strip()
            continue

        if current and re.search(DATE_PATTERN, lower):
            current["duration"] = line
            continue

        if current:
            if line.startswith("-"):
                current["responsibilities"].append(line)
                last_bullet_idx = len(current["responsibilities"]) - 1
            elif last_bullet_idx is not None:
                current["responsibilities"][last_bullet_idx] += " " + line

    if current:
        experiences.append(current)

    return experiences
