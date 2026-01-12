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
    Extract first valid JSON object from LLM output.
    """
    if not text:
        return {}

    try:
        start = text.index("{")
        end = text.rindex("}") + 1
        return json.loads(text[start:end])
    except Exception:
        return {}


def extract_projects_with_llm(project_section_text: str) -> list:
    """
    STRICT project extractor.
    Input:
        project_section_text (str): Raw PROJECTS section text
    Output:
        List of project dictionaries (JSON-safe)
    """

    if not project_section_text or not project_section_text.strip():
        return []

    prompt = f"""
You are a strict resume information extraction engine.

CRITICAL RULES:
- Use ONLY the information explicitly present in the input text.
- DO NOT rewrite, paraphrase, summarize, or reorganize text.
- DO NOT infer meaning or structure.
- DO NOT invent project names, descriptions, or technologies.
- Each numbered or bullet line represents EXACTLY ONE project.
- The FULL original line must be copied verbatim into "description".
- If a field is missing, leave it empty.
- Output MUST be valid JSON ONLY.
- No explanations or extra text.

OUTPUT FORMAT:
{{
  "projects": [
    {{
      "name": "",
      "description": "",
      "techstack": []
    }}
  ]
}}

FIELD RULES:
- "name": Extract ONLY if explicitly stated BEFORE keywords like "using", "with", ":".
- "description": Copy the ENTIRE ORIGINAL PROJECT LINE exactly as written.
- "techstack": Extract ONLY explicitly mentioned technologies; otherwise [].

INPUT (PROJECT SECTION):
<<<
{project_section_text}
>>>
"""

    try:
        response = _client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.0
        )

        response_text = response.choices[0].message.content
        data = _safe_json(response_text)
       

        projects = data.get("projects", [])
        
        return projects if isinstance(projects, list) else []

    except Exception as e:
        
        return []
