
from dotenv import load_dotenv
from fastapi import FastAPI
from temporalio.client import Client
import os

from .router import base,processed_pdf,contract_review


load_dotenv()



app = FastAPI(
    title="Resume Reviewing Client",
    description="Review resume ATS and match score",
    version="1.0",
)



#------ Routers ----------

app.include_router(base.base_router)
app.include_router(processed_pdf.process_app)
app.include_router(contract_review.ContractReviwe)