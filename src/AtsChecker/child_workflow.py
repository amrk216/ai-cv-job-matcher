import textwrap
from dataclasses import dataclass
from datetime import timedelta

import json_repair
from temporalio import workflow
from temporalio.common import RetryPolicy



with workflow.unsafe.imports_passed_through():
    from .DataClasses import (
        PDFSummaryInput,
        PDFSummaryOutput,
    )

    from .prompts import _SUMMARY_PROMPT

     
    from .activites import (
        extract_pdf,
        ExtractPDFInput,
        call_llm,
        CallLLMInput,
        load_job_description 
    )

DEFAULT_RETRY_POLICY = RetryPolicy(
    initial_interval=timedelta(seconds=3),
    backoff_coefficient=2.0,
    maximum_interval=timedelta(seconds=60),
    maximum_attempts=4

)
#----------------workflow--------------
@workflow.defn
class PDFSummaryWorkflow:
    @workflow.run
    async def run(self,params:PDFSummaryInput)->PDFSummaryOutput:


        job_description = await workflow.execute_activity(
        load_job_description,
        params.job_id,
        start_to_close_timeout=timedelta(seconds=30)
    )

        #step 1-> extract pdf content
        extract_md = await workflow.execute_activity(
            extract_pdf,
            ExtractPDFInput(
                s3_path = params.s3_path,
                
                
            ),
            retry_policy = DEFAULT_RETRY_POLICY,
            start_to_close_timeout=timedelta(minutes=20),
            heartbeat_timeout=timedelta(seconds=40)
        )
        # setp -> call llm to summarize to content and extract key risks
        prompt = _SUMMARY_PROMPT.format(
            job_description=job_description,
            resume=extract_md.markdown_text
        )

        llm_result = await workflow.execute_activity(
            call_llm,
            CallLLMInput(prompt=prompt),
            retry_policy = DEFAULT_RETRY_POLICY,
            start_to_close_timeout = timedelta(minutes=20),
            heartbeat_timeout = timedelta(seconds=180)
        )

        parsed_output = json_repair.loads(llm_result.content)
        
        decision = (
        "SHORTLISTED"
        if parsed_output.get("job_match_score", 0) >= 80
        else "REJECTED"
    )

        return PDFSummaryOutput(
            s3_path=params.s3_path,
            candidate_summary=parsed_output.get("candidate_summary", ""),
            ats_score=parsed_output.get("ats_score", 0),
            job_match_score=parsed_output.get("job_match_score", 0),
            decision=decision
        )
