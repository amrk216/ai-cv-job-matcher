from dataclasses import dataclass

#-------------------Activitys----------------
@dataclass
class ExtractPDFInput:
    s3_path:    str
    batch_size: int = 2


@dataclass
class ExtractPDFOutput:
    s3_path:    str
    markdown_text: str
    page_count: int


@dataclass
class CallLLMInput:
    prompt : str

@dataclass 
class CallLLMOutput:
    content: str


#-------------------child Workflow----------------

@dataclass 
class PDFSummaryInput:
    s3_path : str
    job_id:str

@dataclass(frozen=True)
class PDFSummaryOutput:
    s3_path: str
    candidate_summary: str
    ats_score: int
    job_match_score: int
    decision: str



#-------------------Parent Workflow----------------


@dataclass
class ContractReviewInput:
    s3_path : list
    job_id: str
    max_revisions : int = 3 


@dataclass 
class ContractReviewOutput:
    report : str
    source : list
    approved_by : str

