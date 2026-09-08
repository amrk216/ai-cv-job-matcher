# why ??
    1- In parent_workflow.py, why do we use a normal class instead of a dataclass for ContractReviewWorkflow?

            We use a normal class for ContractReviewWorkflow because it contains logic and behavior, not just data.

            The workflow has methods like:

            run() → runs the workflow
            get_status() → gets the workflow status
            submit_decision() → receives approve/revise decisions
            assign_reviewer() → assigns a reviewer

            We use a dataclass for Input and Output because they mainly store data.

            So, simply:

            Dataclass = stores data
            Normal class = contains logic and behavior.



    2- Why do we use asyncio.gather() with start_child_workflow()?

            We use asyncio.gather() to start multiple child workflows at the same time.

            For example, if we have 3 PDF files, we create one PDFSummaryWorkflow for each file:

            PDF 1 → Child Workflow 1
            PDF 2 → Child Workflow 2
            PDF 3 → Child Workflow 3

            asyncio.gather() lets these workflows run in parallel, instead of waiting for the first PDF to finish before starting the second one.

            We also give each child workflow a unique ID:

            id=f"{workflow_id}-pdf-{idx+1}"

            So Temporal can identify each child workflow separately.
