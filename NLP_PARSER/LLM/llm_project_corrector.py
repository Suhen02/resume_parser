
import os
import json
import re
from dotenv import load_dotenv
from huggingface_hub import InferenceClient


load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN not loaded. Check your .env file.")



client = InferenceClient(
    model="mistralai/Mistral-7B-Instruct-v0.2",
    token=HF_TOKEN
)



def _safe_json(text: str) -> dict:
 
    if not text:
        return {}

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return {}

    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return {}


def refine_projects_with_llm(project_section_text: str, projects: list) -> list:
 

    if not project_section_text or not projects:
        return projects

    payload = {
        "project_section_text": project_section_text,
        "projects": projects
    }

    prompt = f"""
        SYSTEM ROLE:
        You are a resume-parsing assistant used in a production ATS system.
        You are NOT allowed to invent information.

        SOURCE OF TRUTH:
        The raw PROJECTS section text is the primary source for project names.

        TASK:
        Correct and refine the project JSON.

        HOW TO HANDLE PROJECT NAMES:
        - Derive or correct project names ONLY from the raw PROJECTS section text
        - If a name is implicit, derive it from described functionality
        - Do NOT invent unrelated names
        - Keep names concise, professional, and resume-ready
        - Ensure all project names are UNIQUE


        STRICT RULES:
        - Do NOT add projects
        - Do NOT remove projects
        - Do NOT merge or split projects
        - Do NOT add or infer technologies
        - Do NOT change meanings
        - Do NOT change project_type
        - Do NOT rewrite descriptions (minor grammar fixes only)
        - If unsure, make the MINIMAL change needed

        INPUT:
        {json.dumps(payload, indent=2)}

        OUTPUT FORMAT (JSON ONLY):
        {{
        "projects": [
            {{
            "name": "<string>",
            "description": "<string>",
            "tech_stack": <list>,
            "project_type": "<string>"
            }}
        ]
        }}

        FINAL CHECK:
        - Project count must match input
        - Every name must be justified by raw PROJECTS text
        - No extra keys allowed
        """

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.25
        )

        response_text = response.choices[0].message.content
        data = _safe_json(response_text)

        refined_projects = data.get("projects")

        if isinstance(refined_projects, list):
            return refined_projects

    except Exception as e:
        print("LLM ERROR:", str(e))

    return projects

