import os
import json
import ast
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



def _safe_json(data):

    if isinstance(data, dict):
        return data

    if not isinstance(data, str) or not data.strip():
        return {}


    if data.count("{") != data.count("}"):
        return {}


    try:
        start = data.index("{")
        end = data.rindex("}") + 1
        return json.loads(data[start:end])
    except Exception:
        pass


    try:
        start = data.index("{")
        end = data.rindex("}") + 1
        return ast.literal_eval(data[start:end])
    except Exception:
        return {}



def _build_examiner_prompt(raw_resume_text, nlp_resume_json, llm_resume_json):
    return f"""
        You are a STRICT resume parsing EXAMINER.

        IMPORTANT OUTPUT CONSTRAINT (MANDATORY):
        - You MUST think silently.
        - You MUST NOT include any text outside the JSON object.
        - Your response MUST start with '{{' and MUST end with '}}'.
        - Use DOUBLE QUOTES for all keys and string values.
        - DO NOT use markdown, bullet points, or explanations.

        YOUR ROLE:
        Compare two parsed resume JSON outputs against the RAW RESUME TEXT
        and decide which approach is MORE CORRECT.

        --------------------------------------------------
        REFERENCE RESUME JSON SCHEMA (MANDATORY)
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
        DECISION FORMAT (MANDATORY)
        --------------------------------------------------

        {{
        "selected_approach": "nlp_heuristic | llm_extraction",
        "reason": "one short factual sentence"
        }}

        --------------------------------------------------
        STRICT EVALUATION RULES
        --------------------------------------------------
        - Raw resume text is the ONLY source of truth.
        - Penalize hallucination, inference, rewriting, or schema violations.
        - Penalize extra or missing entries.
        - Do NOT reward formatting or verbosity.
        - If both outputs contain errors, choose the LESS incorrect one.

        --------------------------------------------------
        INPUT DATA
        --------------------------------------------------

        RAW RESUME TEXT:
        <<<
        {raw_resume_text}
        >>>

        NLP HEURISTIC OUTPUT:
        <<<
        {json.dumps(nlp_resume_json, indent=2)}
        >>>

        LLM EXTRACTION OUTPUT:
        <<<
        {json.dumps(llm_resume_json, indent=2)}
        >>>

        END.
        """



def examine_resume_outputs(
    raw_resume_text: str,
    nlp_resume_json: dict,
    llm_resume_json: dict
) -> dict:
    

    prompt = _build_examiner_prompt(
        raw_resume_text,
        nlp_resume_json,
        llm_resume_json
    )

    def _call_llm(max_tokens: int):
        response = _client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=max_tokens,
            stop=["END."]
        )
        return response.choices[0].message.content

 
    response_text = _call_llm(max_tokens=600)
    decision = _safe_json(response_text)

    if (
        isinstance(decision, dict)
        and decision.get("selected_approach") in {"nlp_heuristic", "llm_extraction"}
        and isinstance(decision.get("reason"), str)
    ):
        return decision

    response_text = _call_llm(max_tokens=1000)
    decision = _safe_json(response_text)

    if (
        isinstance(decision, dict)
        and decision.get("selected_approach") in {"nlp_heuristic", "llm_extraction"}
        and isinstance(decision.get("reason"), str)
    ):
        return decision

    
    return {
        "selected_approach": "nlp_heuristic",
        "reason": "Examiner output was truncated or invalid and could not be parsed safely."
    }
