import json
from extractor.extractor import extract_resume_text
from extractor.utils import clean_text
from NLP_PARSER.section_detector import detect_sections
from NLP_PARSER.skills import extract_skills
from NLP_PARSER.experience import extract_experience
from NLP_PARSER.achievements import extract_achievements
from NLP_PARSER.projects import (
    extract_projects_from_section,
    extract_projects_from_experience
)
from NLP_PARSER.LLM.llm_project_corrector import refine_projects_with_llm
from NLP_PARSER.LLM.llm_project import extract_projects_with_llm

from  NLP_PARSER.LLM.examine_projects_llm import examine_project_outputs
from LLM_PARSER.resume_parser_llm import parse_resume_with_llm


def parse_resume(cleaned_text) -> dict:
  
  

    sections = detect_sections(cleaned_text)

    skills = extract_skills(sections.get("skills", ""))

    experience = (
        extract_experience(sections["experience"])
        if sections.get("experience")
        else []
    )

    projects = []
    if sections.get("projects"):
        projects = extract_projects_from_section(sections["projects"])

    if not projects:
        projects = extract_projects_from_experience(experience)

    
    nlp_projects_section = refine_projects_with_llm(
            project_section_text=sections["projects"],
            projects=projects
        )
    achievements = extract_achievements(sections.get("achievements", ""))
    llm_projects_section=extract_projects_with_llm(sections["projects"])
    final_decision = examine_project_outputs(
            raw_project_section=sections["projects"],
            nlp_projects=nlp_projects_section,
            llm_projects=llm_projects_section
            )
    
    if final_decision["selected_approach"] == "nlp_heuristic":
        final_projects = nlp_projects_section
    else:
        final_projects = llm_projects_section
        
    return{
        "skills": skills,
        "experience": experience,
        "projects": final_projects,
        "achievements": achievements
    }

   
    



