
from pydantic import BaseModel
# ---------- Request / Response Models ----------

class ProcessPDFRequest(BaseModel):
    s3_path: str
    job_id : str
    

class ProcessPDFStartResponse(BaseModel):
    workflow_id: str


class ProcessPDFExecuteResponse(BaseModel):
    workflow_id: str
    results: dict


class StartReviewRequest(BaseModel):
    s3_paths: list[str]
    job_id : str
    max_revisions: int = 2


class AssignRequest(BaseModel):
    name: str


class ReviseRequest(BaseModel):
    feedback: str

class JobDescriptionRequest(BaseModel):
    job_description: str

class JobDescriptionResponse(BaseModel):
    job_id: str
    message: str