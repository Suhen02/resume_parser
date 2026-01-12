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




def examine_project_outputs(
    raw_project_section: str,
    nlp_projects: list,
    llm_projects: list
) -> dict:
    

    prompt = f"""
You are a strict resume parsing EXAMINER.

You are NOT allowed to extract, rewrite, improve, or invent any data.

YOUR ROLE:
Evaluate two project JSON outputs against the RAW PROJECT SECTION
and decide which approach is MORE CORRECT.

--------------------------------------------------
CORRECT PROJECT JSON SCHEMA (REFERENCE)
--------------------------------------------------
Each project MUST follow this structure:

{{
  "name": "<string | empty>",
  "description": "<string copied verbatim from raw text>",
  "techstack": ["<technology>", "..."]
}}

Rules for correctness:
- "description" MUST appear verbatim in the raw project section.
- "name" MUST be justified by the raw text (no invention).
- "techstack" MUST contain ONLY explicitly mentioned technologies.
- No extra keys are allowed.
- No missing required keys are allowed.
- Project count MUST match the raw project section.
--------------------------------------------------

SOURCES PROVIDED:
1) RAW PROJECT SECTION (ground truth)
2) NLP heuristic project JSON
3) LLM extracted project JSON

EVALUATION RULES (MANDATORY):
- Raw project section is the ONLY source of truth.
- Penalize any hallucination, inference, rewriting, or expansion.
- Penalize missing or extra projects.
- Penalize schema violations.
- Penalize invented or inferred technologies.
- If both approaches have errors, select the LESS incorrect one.

DECISION RULE:
Choose EXACTLY ONE:
- "nlp_heuristic"
- "llm_extraction"

OUTPUT FORMAT (STRICT JSON ONLY):
{{
  "selected_approach": "",
  "reason": ""
}}

INPUT DATA:

RAW PROJECT SECTION:
<<<
{raw_project_section}
>>>

NLP HEURISTIC OUTPUT:
<<<
{json.dumps(nlp_projects, indent=2)}
>>>

LLM EXTRACTION OUTPUT:
<<<
{json.dumps(llm_projects, indent=2)}
>>>
"""

    try:
        response = _client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.0
        )

        response_text = response.choices[0].message.content
        decision = _safe_json(response_text)

        if (
            isinstance(decision, dict)
            and decision.get("selected_approach") in {"nlp_heuristic", "llm_extraction"}
        ):
            return decision

    except Exception:
        pass


    return {
        "selected_approach": "nlp_heuristic",
        "reason": "Examiner failed to produce a valid schema-aware decision."
    }
