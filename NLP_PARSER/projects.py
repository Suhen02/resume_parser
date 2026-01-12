
import re

ACTION_VERBS = [
    "built", "developed", "implemented", "designed",
    "created", "integrated", "optimized", "engineered",
    "maintained", "deployed", "automated", "tuned",
    "exported", "enabled"
]



PROJECT_TITLE_HINTS = [
    "system", "application", "app", "platform",
    "generator", "prediction", "recommendation",
    "dashboard", "web", "portal", "tool",
    "chatbot", "model"
]



TECH_HINTS = [
    "python", "java", "javascript", "typescript",
    "c++", "c#", "go", "php", "ruby",
    "react", "angular", "vue", "html", "css",
    "flask", "django", "fastapi", "spring",
    "node", "express",

    "mysql", "postgres", "mongodb", "redis",
    
    "docker", "kubernetes", "aws", "azure", "gcp",
 
    "machine learning", "ml", "deep learning",
    "nlp", "rag", "tensorflow", "pytorch",
    "xgboost", "lstm", "cnn", "transformer",

    "git", "github", "ci/cd", "linux"
]



def is_project_title(line: str) -> bool:
    """
    Robust detection of project titles.
    Handles hyphens, parentheses, mixed casing.
    """
    if not line:
        return False

    if line.startswith(("-", "•")):
        return False


    if len(line) > 120:
        return False

    lower = line.lower()

    if any(v in lower for v in ACTION_VERBS):
        return False


    if any(h in lower for h in PROJECT_TITLE_HINTS):
        return True

    if re.match(r"^[A-Z][A-Za-z0-9 &\-()–]+$", line):
        return True

    return False


def is_tech_line(line: str) -> bool:

    if line.startswith(("-", "•")):
        return False

    lower = line.lower()

    return (
        "," in line
        and len(line.split(",")) >= 2
        and not any(v in lower for v in ACTION_VERBS)
    )


def looks_like_wrapped_line(line: str) -> bool:

    return (
        line
        and (line[0].islower() or line[0] in ",.;)")
    )


def extract_tech_stack(text: str) -> list:
 
    found = set()
    lower = text.lower()

    for tech in TECH_HINTS:
        if re.search(r"\b" + re.escape(tech) + r"\b", lower):
            found.add(tech.title())

    return sorted(found)


def extract_projects_from_section(text: str) -> list:

    projects = []
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    current = None
    collecting_description = False

    for line in lines:

        if current and looks_like_wrapped_line(line):
            current["description"] += " " + line
            collecting_description = True
            continue

        if is_project_title(line) and not collecting_description:
            if current:
                projects.append(current)

            current = {
                "name": line,
                "description": "",
                "tech_stack": []
            }
            collecting_description = False
            continue

        if current and is_tech_line(line):
            current["tech_stack"].extend(extract_tech_stack(line))
            continue

        if current:
            clean = line.lstrip("•- ").strip()
            if clean:
                current["description"] += (
                    " " + clean if current["description"] else clean
                )
                collecting_description = True

    if current:
        projects.append(current)

    return projects


def extract_projects_from_experience(experience: list) -> list:
    """
    Fallback project extraction from experience bullets.
    """
    projects = []

    for exp in experience:
        for bullet in exp.get("responsibilities", []):
            clean = bullet.lstrip("•- ").strip()
            lower = clean.lower()

            if (
                any(v in lower for v in ACTION_VERBS)
                and any(h in lower for h in PROJECT_TITLE_HINTS)
            ):
                projects.append({
                    "name": "Derived Project",
                    "description": clean,
                    "tech_stack": extract_tech_stack(clean)
                })

    return projects
