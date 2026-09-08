import json
import textwrap
from dataclasses import dataclass
from datetime import timedelta
import asyncio
from typing import Optional

import json_repair
from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import ApplicationError
from temporalio.workflow import ParentClosePolicy



with workflow.unsafe.imports_passed_through():
    
    from .DataClasses import ContractReviewInput, ContractReviewOutput
    from .prompts import _SYNTHESIS_PROMPT, _REVISION_PROMPT

    from .activites import (
        call_llm,
        CallLLMInput,
    )

    from .child_workflow import (
        PDFSummaryWorkflow,
        PDFSummaryInput,
    )
DEFAULT_RETRY_POLICY = RetryPolicy(
    initial_interval=timedelta(seconds=3),
    backoff_coefficient=2.0,
    maximum_interval=timedelta(seconds=60),
    maximum_attempts=4
)

@workflow.defn
class ContractReviewWorkflow: # why we used just normal class, answer in whyqu.md (1)
    def __init__(self):
        self._status : str = "processing"
        self._summaries : list = []
        self._report: str = ""

        self._review_decision: Optional[str] = None
        self._review_feedback: str = ""
        self._approved_by: str = ""


    # Query : status of the workflow
    @workflow.query
    def get_status(self) -> dict:
        return{
            "status" : self._status,
            "files_processed" : len(self._summaries),
            "report_ready" : json.dumps(self._report,ensure_ascii=False),
            "approved_by" : self._approved_by
        }



    @workflow.query
    def get_report(self) -> dict:
        return {
            "status": self._status,
            "report": self._report,
            "approved_by": self._approved_by,
            "source": [s["s3_path"] for s in self._summaries]
        } 

    @workflow.signal
    async def assign_reviwer(self,name:str):
        self._approved_by = name


    @workflow.update
    async def submit_decision(self,decision:str,feedback:str="")-> str:
        self._review_decision = decision
        self._review_feedback = feedback

        return f"Decision '{decision}' recorder " 

    @submit_decision.validator
    def validate_decision(self, decision:str, feedback:str="")->None:
        if decision not in ("approve","revise"):
            raise ValueError(f"Must be 'approve' or 'revise' , got '{decision}'")
        if decision == "revise" and not feedback.strip():
            raise ValueError(f'FeedBack is required when requesting revision')

    @workflow.run
    async def run(self,params:ContractReviewInput)->ContractReviewOutput:
        self._status = "extracting....."

        workflow.logger.info(f"Fanning out to {len(params.s3_path)} child")

        workflow_id = workflow.info().workflow_id
        workflow_task_queue = workflow.info().task_queue

        handels = await asyncio.gather( # why used asyncio.gather with start_child_workflow? answer in whyqu.md (2)

            *[   
                workflow.start_child_workflow(
                    PDFSummaryWorkflow.run,
                    PDFSummaryInput(
                        s3_path=current_s3_path,
                        job_id=params.job_id
                        ),
                    id=f'{workflow_id}-pdf-{idx+1}',
                    task_queue= workflow_task_queue,
                    parent_close_policy=ParentClosePolicy.ABANDON #Abandon: the Child Workflow Execution is not affected.
                )
                
                for idx , current_s3_path in enumerate(params.s3_path)
            ]   
        )

        row_result = await asyncio.gather(
            *handels,
            return_exceptions=True
        )

        for i , res in enumerate(row_result):
            if isinstance(res,Exception):
                workflow.logger.error(f'PDF {i} faild : res{res}')

            else:
                self._summaries.append({
                "s3_path": res.s3_path,
                "candidate_summary": res.candidate_summary,
                "ats_score": res.ats_score,
                "job_match_score": res.job_match_score,
                "decision": res.decision,
                })

        if len(self._summaries) == 0 :
            raise ApplicationError("All child workflows faild")




        # Step 2 : Synthesize the summaries into a single report

        self._status = "synthesizing"
        workflow.logger.info(f'summarizing {len(self._summaries)} summaries')

        combined_summaries = "\n\n".join([
                f"""**Candidate {i+1} ({summary['s3_path']})**
            Candidate Summary:
            {summary['candidate_summary']}

            ATS Score:
            {summary['ats_score']}

            Job Match Score:
            {summary['job_match_score']}

            Decision:
            {summary['decision']}
            """
                for i, summary in enumerate(self._summaries)
            ])


        llm_prompt = _SYNTHESIS_PROMPT.format(
            summaries=combined_summaries,
            n=len(self._summaries)
        )

        llm_result = await workflow.execute_activity(
            call_llm,
            CallLLMInput(prompt=llm_prompt),
                retry_policy=DEFAULT_RETRY_POLICY,
                start_to_close_timeout=timedelta(minutes=3),
                heartbeat_timeout=timedelta(seconds=180)
        )

        self._report = json_repair.loads(llm_result.content)

        for revision_no in range(params.max_revisions+1):

            self._status = "awaiting_review"
            workflow.logger.info(f"Awaiting review for human review {revision_no}")

            self._review_decision = None


            try: 
                await workflow.wait_condition(
                    lambda: self._review_decision is not None,
                    timeout=timedelta(days=3),
                )
            except asyncio.TimeoutError:
                workflow.logger.warning("Review timed out after 3 days, proceeding with current report")
                break

            if self._review_decision == "approve":
                workflow.logger.info("Report approved by reviewer")
                self._approved_by = workflow.info(f"Report approved by reviewer: {self._approved_by}").workflow_id
                break

            self._status = "revising"
            workflow.logger.info(f"Revision requested by reviewer: {self._review_feedback}")

            llm_prompt = _REVISION_PROMPT.format(
                report = json.dumps(self._report, indent=2,ensure_ascii=False),
                feedback = self._review_feedback
            )

            revised_report = await workflow.execute_activity(
                call_llm,
                CallLLMInput(prompt=llm_prompt),
                    retry_policy=DEFAULT_RETRY_POLICY,
                    start_to_close_timeout=timedelta(minutes=3),
                    heartbeat_timeout=timedelta(seconds=180)
            )

            self._report = json_repair.loads(revised_report.content)
            # Revicsion completed, loop back to await review again
        self._status = "completed"
        return ContractReviewOutput(
                report = self._report,
                source = [s["s3_path"] for s in self._summaries],
                approved_by = self._approved_by
            )

    