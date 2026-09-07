from dotenv import load_dotenv
from fastapi import FastAPI,APIRouter, HTTPException
from temporalio.client import Client
from temporalio.client import WorkflowExecutionStatus as WES    
from fastapi import APIRouter

from AtsChecker.helpers import save_job_description



from ..schemas.PydanticModels import (
    JobDescriptionRequest,
    JobDescriptionResponse,
    ProcessPDFExecuteResponse,
    ProcessPDFRequest,
    ProcessPDFStartResponse,
)

from ..dependencies.temporal import (
    get_temporal_client,
    TEMPORAL_CONTRACT_REVIEW_TASK_QUEUE
)

import uuid
import os
import uuid

import logging
logger = logging.getLogger('uvicorn.error')

process_app = APIRouter(
    prefix="/api",
    tags=["process"],
)

@process_app.post(
    "/job-description",
    response_model=JobDescriptionResponse
)
async def create_job(request: JobDescriptionRequest):

    if not request.job_description:
        raise HTTPException(
            status_code=400,
            detail="Job description is required"
        )

    job_description = request.job_description.strip()

    if len(job_description) < 50:
        raise HTTPException(
            status_code=400,
            detail="Job description is too short"
        )

    job_id = f"job-{uuid.uuid4()}"

    s3_path = save_job_description(
        job_id,
        job_description
    )

    return JobDescriptionResponse(
        job_id=job_id,
        message="Job description created successfully"
    )


@process_app.post("/proccess_pdf/execute", response_model = ProcessPDFExecuteResponse)
async def process_pdf(request:ProcessPDFRequest):

    workflow_id = f'PDF_Pipeline-{uuid.uuid4()}'

    client = await get_temporal_client()

    results = await client.execute_workflow(
        "PDFSummaryWorkflow",

        args=[
            {
                "s3_path":request.s3_path,
                "job_id": request.job_id
                
                
            }
        ],
        
        id = workflow_id,
        task_queue= TEMPORAL_CONTRACT_REVIEW_TASK_QUEUE,
        result_type= dict 
    )
    return ProcessPDFExecuteResponse(
        workflow_id=workflow_id,
        results=results
    )

@process_app.post("/process_pdf/start",response_model=ProcessPDFStartResponse)
async def process_pdf(request:ProcessPDFRequest):
    workflow_id = f'PDF_Pipeline-{uuid.uuid4()}'
    
    client = await get_temporal_client()

    results = await client.start_workflow( # start workflow
        "PDFSummaryWorkflow",

        args=[
            {
                "s3_path":request.s3_path,
                "job_id": request.job_id
                
            }
        ],
        id = workflow_id,
        task_queue= TEMPORAL_CONTRACT_REVIEW_TASK_QUEUE,
        result_type= dict 
    )
    return ProcessPDFStartResponse(
        workflow_id=workflow_id,
        
    )


@process_app.get("/workflow/status/{workflow_id}")
async def get_work_status(workflow_id):
    client = await get_temporal_client()
    handel = client.get_workflow_handle(workflow_id)
    desc = await handel.describe()

    try:
        result = await handel.result()
    except Exception:
        result = None


    workflow_status = desc.status

    return{
        "workflow_id": workflow_id,
        "workflow_status": workflow_status.name.capitalize(),
        "workflow_result": result
    }
