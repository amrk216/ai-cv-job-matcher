from dotenv import load_dotenv
from fastapi import FastAPI,APIRouter
from temporalio.client import Client
from temporalio.client import WorkflowExecutionStatus as WES    
from ..schemas.PydanticModels import (
    AssignRequest,
    ProcessPDFStartResponse,
    ReviseRequest,
    StartReviewRequest
)

from ..dependencies.temporal import (
    get_temporal_client,
    TEMPORAL_CONTRACT_REVIEW_TASK_QUEUE,

)
import os
import uuid

import logging
logger = logging.getLogger('uvicorn.error')

ContractReviwe = APIRouter(
    prefix="/api",
    tags=["ContractReviwe"],
)


@ContractReviwe.post("/contract-review/start",response_model=ProcessPDFStartResponse)
async def start_contract_review(request:StartReviewRequest):

    workflow_id = f"contract-review-{uuid.uuid4()}"

    client = await get_temporal_client()

    await client.start_workflow(
        "ContractReviewWorkflow",
        args=[
            {
                "s3_path": request.s3_paths,
                "job_id": request.job_id,
                "max_revisions": request.max_revisions
            }
        ],
        id = workflow_id,
        task_queue = TEMPORAL_CONTRACT_REVIEW_TASK_QUEUE,
        )

    return ProcessPDFStartResponse(
        
        workflow_id=workflow_id
    )


@ContractReviwe.get("/contract-review/{workflow_id}/status")
async def get_review_status(workflow_id: str):
    client = await get_temporal_client()
    handle = client.get_workflow_handle(workflow_id)
    desc = await handle.describe()

    workflow_status = None
    if desc.status == WES.RUNNING:
        try:
            workflow_status = await handle.query("get_status", result_type=dict)
        except Exception as e:
            workflow_status = {"error": str(e)}

    return {
        "workflow_id": workflow_id,
        "workflow_status": desc.status.name,
        "workflow_details": workflow_status
    }


@ContractReviwe.get("/contract-review/{workflow_id}/report")
async def get_review_status(workflow_id: str):
    client = await get_temporal_client()
    handle = client.get_workflow_handle(workflow_id)
    desc = await handle.describe()

    workflow_status = None
    if desc.status == WES.RUNNING:
        try:
            workflow_status = await handle.query("get_report", result_type=dict)
        except Exception as e:
            workflow_status = {"error": str(e)}

    return {
        "workflow_id": workflow_id,
        "workflow_status": desc.status.name,
        "workflow_details": workflow_status,
    }


@ContractReviwe.post("/contract-review/{workflow_id}/assign-reviewer")
async def assign_reviewer(workflow_id: str, request: AssignRequest):
    client = await get_temporal_client()
    handle = client.get_workflow_handle(workflow_id)

    await handle.signal("assign_reviewer", request.name)

    return {
        "status": "success",
        "workflow_id": workflow_id,
        "message": f"Reviewer '{request.name}' assigned to workflow."}



@ContractReviwe.post("/contract-review/{workflow_id}/revise")
async def submit_revision(workflow_id: str, request: ReviseRequest):
    client = await get_temporal_client()
    handle = client.get_workflow_handle(workflow_id)

    result = await handle.execute_update(
        "submit_decision",
        args=[ "revise", request.feedback],
       
    )

    return {
        "status": "success",
        "workflow_id": workflow_id,
        "message": result
    }

@ContractReviwe.get("/contract-review/{workflow_id}/approve")
async def approve_review(workflow_id: str):
    client = await get_temporal_client()
    handle = client.get_workflow_handle(workflow_id)

    result = await handle.execute_update(
        "submit_decision",
        args=[ "approve", ""],
       
    )

    return {
        "status": "success",
        "workflow_id": workflow_id,
        "message": result
    }