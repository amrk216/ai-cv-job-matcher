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



def compare_cv_with_job(cv_text:str, job_description:str)->str:

    response = llm_client.chat.completions.create(
        model=MODEL_NAME,
        
        messages=[
            {"role": "system", "content": system_message.format(job_description=job_description, cv=cv_text)},
            
        ],
        extra_body={"thinking": { "type": "disabled" }}
        

        
    
    )
    content= response.choices[0].message.content

    content = re.sub(
        r"<think>.*?</think>\s*",
        "",
        content,
        flags=re.DOTALL,

    )
    return content






