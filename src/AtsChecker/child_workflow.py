import textwrap
from dataclasses import dataclass
from datetime import timedelta

import json_repair
from temporalio import workflow
from temporalio.common import RetryPolicy
from DataClasses import PDFSummaryInput,PDFSummaryOutput
from helpers import DEFAULT_RETRY_POLICY
from prompts import _SUMMARY_PROMPT
with workflow.unsafe.imports_passed_through():
    from activites import(
        extract_pdf,ExtractPDFInput,
        call_llm,CallLLMInput
    )

#----------------workflow--------------
@workflow.defn
class PDFSummaryWorkflow:
    @workflow.run
    async def run(param:PDFSummaryInput)->PDFSummaryOutput:

        #step 1-> extract pdf content
        extract_md = await workflow.execute_activity(
            extract_pdf,
            ExtractPDFInput(
                s3_path = param.s3_path
            ),
            retry_policy = DEFAULT_RETRY_POLICY,
            start_to_close_timeout=timedelta(minutes=20),
            heartbeat_timeout=timedelta(seconds=40)
        )
        # setp -> call llm to summarize to content and extract key risks
        prompt = _SUMMARY_PROMPT.format(
            text = extract_md.markdown_text[0:]
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
            s3_path=param.s3_path,
            candidate_summary=parsed_output.get("candidate_summary", ""),
            ats_score=parsed_output.get("ats_score", 0),
            job_match_score=parsed_output.get("job_match_score", 0),
            decision=decision
        )
