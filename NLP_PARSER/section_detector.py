
import re

SECTION_HEADERS = {
    "skills": [
        "skills", "technical skills", "technologies", "tech stack","tech skills", "skill set",
        "tools"
    ],
    "experience": [
        "experience","internships", "professional experience", "work experience", "professional experience",
        "employment", "industry experience","Work History",'work history'
    ],
    "projects": [
        "projects", "academic projects", "personal projects",
         "project", "project work", "key projects",
        "academic projects", "project experience"
    ],
    "education": [
        "education", "academic background", "qualification"
    ],
    "achievements": [
        "achievements", "awards", "certifications",
        "achievements & certificates", "honors", "recognition",
        "certifications", "accomplishments","Achievements & Certificates",'ACHIEVEMENTS & CERTIFICATES','achievements & certificates'
    ],
    "summary": [
        "summary", "profile", "objective"
    ]
}



def normalize(text: str) -> str:
    return re.sub(r"[^a-z& ]", "", text.lower()).strip()


def match_section_header(line: str):
    norm = normalize(line)

    for section, headers in SECTION_HEADERS.items():
        for h in headers:
            if norm == h:
                return section
    return None




def detect_sections(text: str) -> dict:

    lines = [l.strip() for l in text.split("\n") if l.strip()]
    sections = {}
    current_section = None
    buffer = []

    for line in lines:
        detected = match_section_header(line)

        if detected:
        
            if current_section:
                sections[current_section] = "\n".join(buffer)

            current_section = detected
            buffer = []
            continue

        if current_section:
            buffer.append(line)


    if current_section and buffer:
        sections[current_section] = "\n".join(buffer)

    return sections
