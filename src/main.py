import logging
from pathlib import Path
import shutil

from fastapi import FastAPI, Form,UploadFile,File
from processing import process_cv,compare_cv_with_job
from prompt import system_message,job_description2
logger = logging.getLogger('uvicorn.error')
app = FastAPI(
    title="PDF Extraction Client",
    version="0.1"
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/health")
async def health():
    return{
        "status":"200 ok"
    }


@app.post("/upload_cv")
async def upload_cv(file:UploadFile=File(...),job_description:str=Form(...)):
    logger.info("---------------Starting uploading file...--------------------")
    file_path = UPLOAD_DIR / file.filename

    with open(file_path,"wb") as buffer:
        shutil.copyfileobj(file.file,buffer)

    cv_text = process_cv(str(file_path))

    result = compare_cv_with_job(cv_text=cv_text,job_description=job_description)

    return{
        "Filename":file.filename,
        "content": result
    }


