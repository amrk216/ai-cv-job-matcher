import re

import pymupdf
import os
import pymupdf4llm
from dotenv import load_dotenv
from openai import OpenAI
from prompt import system_message, job_description2
from headers_cv import SKILL_HEADERS,EXPERIENCE_HEADERS,EDUCATION_HEADERS,PROJECT_HEADERS,CERTIFICATION_HEADERS

load_dotenv()
MY_CV= os.environ["MY_CV"]
API_KEY= os.environ["API_KEY"]
MODEL_NAME= os.environ["MODEL_NAME"]
BASE_URL = os.environ["BASE_URL"]

llm_client = OpenAI(
        api_key = API_KEY,
        base_url = BASE_URL
    )

def clean_cv(cv_text:str):
    liens = [line.strip() for line in cv_text.splitlines() if line.strip()]
    
    return "\n".join(liens)

def process_cv(file_path:str)->str:
    cleaning_cv = clean_cv(pymupdf4llm.to_markdown(file_path)) 
    print(cleaning_cv)
    return cleaning_cv


# def extract_cv_sections(cv_text:str):

#     section = {
#         "skills":"",
#         "experience":"",
#         "education":"",
#         "projects":"",
#         "certifications":""
#     }
#     current_section = None

#     headers = {
#         "skills": {h.strip().lower() for h in SKILL_HEADERS},
#         "experience": {h.strip().lower() for h in EXPERIENCE_HEADERS},
#         "education": {h.strip().lower() for h in EDUCATION_HEADERS},
#         "projects": {h.strip().lower() for h in PROJECT_HEADERS},
#         "certifications": {h.strip().lower() for h in CERTIFICATION_HEADERS},
#     }

#     for line in cv_text.splitlines():
#         line = line.strip()
#         lower_line = line.lower()

#         if not line:
#             continue


    
#         # Check if this line is a section header
#         if lower_line in headers["skills"]:
#             current_section = "skills"
#             continue

#         elif lower_line in headers["experience"]:
#             current_section = "experience"
#             continue

#         elif lower_line in headers["education"]:
#             current_section = "education"
#             continue

#         elif lower_line in headers["projects"]:
#             current_section = "projects"
#             continue

#         elif lower_line in headers["certifications"]:
#             current_section = "certifications"
#             continue

#         if current_section:
#             section[current_section]+= line + "\n"


#     return section






def compare_cv_with_job(cv_text:str, job_description:str)->str:



    # sections = extract_cv_sections(cv_text)

    # structured_cv = f"""
    #     Skills:
    #     {sections["skills"]}

    #     Experience:
    #     {sections["experience"]}

    #     Education:
    #     {sections["education"]}

    #     Projects:
    #     {sections["projects"]}

    #     Certifications:
    #     {sections["certifications"]}
    #     """
    # print(structured_cv)
    response = llm_client.chat.completions.create(
        model=MODEL_NAME,
        
        messages=[
            {"role": "system", "content": system_message.format(job_description=job_description, cv=cv_text)},
            
        ],
        extra_body={"thinking": { "type": "disabled" }}
        

        
    
    )
    content= response#.choices[0].message.content

    # content = re.sub(
    #     r"<think>.*?</think>\s*",
    #     "",
    #     content,
    #     flags=re.DOTALL,

    # )
    return content






