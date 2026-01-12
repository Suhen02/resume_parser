from flask import Flask,request
from NLP_PARSER.main import parse_resume
from LLM_PARSER.resume_parser_llm import parse_resume_with_llm
from extractor.extractor import extract_resume_text
from extractor.utils import clean_text
from resume_examiner_llm import examine_resume_outputs
import json
import os

app=Flask(__name__)
UPLOAD_FOLDER = "./uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/resume_parser',methods=['POST'])
def main():
    try:
        resume=request.files.get('resume')
    except Exception as e:
        raise e  
      
    if resume:
        #resume.save(f"./uploads/{resume.filename}")
        file_path = os.path.join(UPLOAD_FOLDER, resume.filename)
        resume.save(file_path)

    else:
        return "NO files are recived."
    try:
        
        raw_text=extract_resume_text(f'./uploads/{resume.filename}')
        cleaned_text=clean_text(raw_text)
        nlp_parsed_resume=parse_resume(cleaned_text)
        llm_parsed_resume=parse_resume_with_llm(cleaned_text)
        decision = examine_resume_outputs(
            raw_resume_text=cleaned_text,
            nlp_resume_json=nlp_parsed_resume,
            llm_resume_json=llm_parsed_resume
        )
        final_resume = (
            nlp_parsed_resume
            if decision["selected_approach"] == "nlp_heuristic"
            else llm_parsed_resume
        )

        return json.dumps(final_resume, indent=4, ensure_ascii=False)
    except Exception as e:
        raise e

if __name__=='__main__':   
    app.run(debug=True) 