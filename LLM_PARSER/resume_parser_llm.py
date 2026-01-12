import os
import json
from dotenv import load_dotenv
from huggingface_hub import InferenceClient



load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    raise RuntimeError("HF_TOKEN not loaded. Check your .env file.")



_client = InferenceClient(
    model="mistralai/Mistral-7B-Instruct-v0.2",
    token=HF_TOKEN
)


def _safe_json(text: str) -> dict:
    """
    Extract valid JSON object only if complete and parsable.
    """
    if not text:
        return {}

    if text.count("{") != text.count("}") or text.count("[") != text.count("]"):
        return {}

    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        return json.loads(text[start:end])
    except Exception:
        return {}



def parse_resume_with_llm(resume_text: str) -> dict:
  
    if not resume_text or not resume_text.strip():
        return {
            "experience": [],
            "projects": [],
            "skills": [],
            "achievements": []
        }

    prompt = f"""
        You are a STRICT resume information extraction engine.

        YOU MUST FOLLOW THESE RULES EXACTLY:

        GLOBAL RULES:
        - Use ONLY information explicitly present in the resume text.
        - DO NOT add, infer, guess, rewrite, or improve any content.
        - DO NOT merge, split, or fabricate entries.
        - DO NOT invent skills, companies, roles, metrics, or technologies.
        - If a field is missing, return an empty list.
        - Output MUST be valid JSON ONLY.
        - No explanations, comments, or extra text.

        --------------------------------------------------
        CORRECT OUTPUT SCHEMA (MANDATORY)
        --------------------------------------------------

        {{
        "experience": [
            {{
            "company": "",
            "role": "",
            "duration": "",
            "description": ""
            }}
        ],
        "projects": [
            {{
            "name": "",
            "description": "",
            "techstack": []
            }}
        ],
        "skills": [],
        "achievements": []
        }}

        --------------------------------------------------
        SECTION-SPECIFIC RULES
        --------------------------------------------------

        EXPERIENCE:
        - Extract ONLY work/internship experience.
        - "description" must be copied verbatim from resume.
        - If company, role, or duration is not explicitly stated, leave it empty.

        PROJECTS:
        - Each bullet or numbered project = ONE project.
        - "description" MUST be copied verbatim.
        - "name" ONLY if explicitly stated.
        - "techstack" ONLY if explicitly mentioned.

        SKILLS:
        - Extract skills ONLY if listed explicitly.
        - No inferred or categorized skills.

        ACHIEVEMENTS:
        - Extract awards, recognitions, rankings, or accomplishments.
        - Copy text verbatim.

        --------------------------------------------------
        INPUT RESUME TEXT
        --------------------------------------------------
        <<<
        {resume_text}
        >>>
        """

    try:
        response = _client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1200,
            temperature=0.0  
        )

        response_text = response.choices[0].message.content
        data = _safe_json(response_text)

        
        return {
            "skills": data.get("skills", []) if isinstance(data.get("skills"), list) else [],
            "experience": data.get("experience", []) if isinstance(data.get("experience"), list) else [],
            "projects": data.get("projects", []) if isinstance(data.get("projects"), list) else [],
            "achievements": data.get("achievements", []) if isinstance(data.get("achievements"), list) else []
        }

    except Exception:
       
        return {
            "skills": [],
            "experience": [],
            "projects": [],
            "achievements": []
        }
