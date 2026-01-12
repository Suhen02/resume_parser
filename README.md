# Resume Parsing & Examination System  
**Hybrid NLP + LLM | Hallucination-Safe | Flask API**

---

## 1. Project Overview

This project implements a **production-grade resume parsing system** that converts unstructured resume text into structured JSON **without hallucination**.

Unlike naïve LLM-based parsers, this system uses a **hybrid architecture**:

- Rule-based / NLP heuristic parsing  
- Strict LLM-based extraction  
- LLM-based examiner (arbiter)  
- Robust JSON validation  
- Flask API for external integration  

The system guarantees:
- No invented data  
- Schema correctness  
- Deterministic outputs  
- Safe handling of LLM failures  

---

## 2. Why This Project Exists

LLMs are powerful but unreliable for structured extraction:

- They hallucinate  
- They truncate JSON  
- They rewrite content  
- They return non-JSON outputs  

This project solves those problems by:

- Treating LLMs as **extractors**, not generators  
- Validating everything against raw resume text  
- Using an **examiner LLM** to arbitrate correctness  
- Enforcing strict schemas at every stage  

---

## 3. High-Level Architecture

Raw Resume Text
|
v
Section Detection
|
+-----------------------+
| |
v v
NLP Heuristic Parser LLM Strict Extractor
| |
+-----------+-----------+
|
v
Resume Examiner LLM
|
v
Final Parsed Resume JSON
|
v

