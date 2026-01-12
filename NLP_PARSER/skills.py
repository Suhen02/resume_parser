
import re

SKILL_CATEGORIES = {
    "programming_languages": [
        "python", "java", "c", "c++", "c#", "javascript", "typescript",
        "go", "rust", "php", "ruby", "kotlin", "swift", "scala"
    ],
    "backend_frameworks": [
        "flask", "django", "fastapi", "spring", "spring boot",
        "node.js", "express", "nestjs"
    ],
    "frontend_technologies": [
        "html", "css", "javascript", "react", "angular", "vue",
        "next.js", "tailwind", "bootstrap"
    ],
    "databases": [
        "mysql", "postgresql", "sqlite", "mongodb", "redis",
        "oracle", "sql server", "cassandra"
    ],
    "devops_cloud": [
        "docker", "kubernetes", "aws", "azure", "gcp",
        "terraform", "jenkins", "github actions", "ci/cd"
    ],
    "ml_ai": [
        "machine learning", "deep learning", "nlp", "computer vision",
        "tensorflow", "pytorch", "scikit-learn", "keras",
        "llm", "rag", "transformers"
    ],
    "data_tools": [
        "pandas", "numpy", "matplotlib", "seaborn", "spark",
        "hadoop", "airflow"
    ],
    "tools_platforms": [
        "git", "github", "gitlab", "linux", "bash",
        "postman", "jira", "confluence"
    ],
    "apis_protocols": [
        "rest", "rest api", "graphql", "grpc", "soap"
    ]
}


def extract_skills(text: str) -> list:
   

    if not text:
        return []

    text_lower = text.lower()
    found_skills = set()

    for _, skills in SKILL_CATEGORIES.items():
        for skill in skills:
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, text_lower):
                found_skills.add(skill.title())

    return sorted(found_skills)
