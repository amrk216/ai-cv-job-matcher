# Resume Reviewing Client

An AI-powered Resume Reviewing and ATS Job Matching system built with
**FastAPI**, **Temporal**, **S3-compatible object storage**, **PyMuPDF /
pymupdf4llm**, and an **LLM**.

The system receives a Job Description and multiple candidate resumes,
processes the resumes in parallel, evaluates each candidate against the
job requirements, and produces an aggregated review report that can go
through a human approval/revision cycle.

## Features

-   Job Description creation and persistent storage.
-   Resume storage in S3-compatible object storage.
-   PDF resume extraction and conversion to Markdown.
-   LLM-based resume analysis.
-   ATS Score generation.
-   Job Match Score generation.
-   Candidate decision:
    -   `SHORTLISTED`
    -   `REJECTED`
-   Parallel resume processing using **Temporal Child Workflows**.
-   Aggregation of multiple candidate results.
-   LLM-based final report synthesis.
-   Human-in-the-loop review.
-   Reviewer assignment.
-   Approve / Revise workflow.
-   Multiple revision cycles.
-   Workflow status and report APIs.
-   FastAPI Swagger/OpenAPI documentation.

## Architecture

``` text
                    ┌──────────────────────┐
                    │       FastAPI        │
                    │      REST API        │
                    └──────────┬───────────┘
                               │
              ┌────────────────┴────────────────┐
              │                                 │
              ▼                                 ▼
       Job Description                    Contract Review
          Storage                           Workflow
              │                                 │
              ▼                         ┌───────┴────────┐
        S3 / Object                     │                │
          Storage                       ▼                ▼
                                  PDFSummaryWorkflow  PDFSummaryWorkflow
                                      (CV 1)             (CV 2)
                                           │                │
                                           └──────┬─────────┘
                                                  │
                                                  ▼
                                           PDFSummaryWorkflow
                                                (CV N)
                                                  │
                                                  ▼
                                           LLM Evaluation
                                                  │
                                                  ▼
                                         Candidate Summaries
                                                  │
                                                  ▼
                                          Synthesis LLM
                                                  │
                                                  ▼
                                          Reviewable Report
                                                  │
                                      ┌───────────┴───────────┐
                                      │                       │
                                   Approve                  Revise
                                      │                       │
                                      ▼                       ▼
                                  Completed              LLM Revision
                                                              │
                                                              └──► Review
```

## Workflow Design

### 1. Job Description

A Job Description is created through the API and assigned a unique
`job_id`.

The Job Description is stored in S3 under:

``` text
jobs/{job_id}.txt
```

The `job_id` is later passed to the workflow instead of sending the full
Job Description repeatedly.

### 2. ContractReviewWorkflow

The main workflow receives:

``` json
{
  "s3_path": [
    "s3://ats/cvs/cv1.pdf",
    "s3://ats/cvs/cv2.pdf",
    "s3://ats/cvs/cv3.pdf"
  ],
  "job_id": "job-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "max_revisions": 2
}
```

It then starts one `PDFSummaryWorkflow` child workflow for each resume.

This allows the resumes to be processed independently and in parallel.

### 3. PDFSummaryWorkflow

Each child workflow:

1.  Loads the Job Description using `job_id`.
2.  Downloads the resume from S3.
3.  Extracts the PDF content.
4.  Converts the extracted content into Markdown.
5.  Sends the resume and Job Description to the LLM.
6.  Parses the structured LLM response.
7.  Calculates the candidate decision based on the Job Match Score.
8.  Returns the candidate evaluation to the parent workflow.

Example decision logic:

``` text
Job Match Score >= 80  →  SHORTLISTED
Job Match Score < 80   →  REJECTED
```

### 4. Report Synthesis

After all child workflows finish, `ContractReviewWorkflow` combines
their results and sends them to a synthesis LLM.

The synthesis stage produces a final candidate evaluation report.

### 5. Human Review

The workflow then enters:

``` text
awaiting_review
```

A reviewer can:

-   Assign a reviewer.
-   Approve the report.
-   Request a revision.
-   Provide revision feedback.

If the reviewer requests a revision, the report is sent back to the LLM
and the workflow returns to the review stage.

The number of revision cycles is controlled by:

``` json
"max_revisions": 2
```

The workflow remains running while waiting for human review.

## API

The application exposes the following endpoints.

### General

  Method   Endpoint     Description
  -------- ------------ ----------------------
  `GET`    `/api/v1/`   API welcome endpoint

### Job & Resume Processing

  --------------------------------------------------------------------------------------
  Method                  Endpoint                               Description
  ----------------------- -------------------------------------- -----------------------
  `POST`                  `/api/job-description`                 Create and store a Job
                                                                 Description

  `POST`                  `/api/process_pdf/execute`             Execute PDF processing
                                                                 and wait for workflow
                                                                 completion

  `POST`                  `/api/process_pdf/start`               Start PDF processing
                                                                 asynchronously

  `GET`                   `/api/workflow/status/{workflow_id}`   Get workflow status
  --------------------------------------------------------------------------------------

### Contract Review

  ------------------------------------------------------------------------------------------------------
  Method                  Endpoint                                               Description
  ----------------------- ------------------------------------------------------ -----------------------
  `POST`                  `/api/contract-review/start`                           Start the Contract
                                                                                 Review workflow

  `GET`                   `/api/contract-review/{workflow_id}/status`            Get review workflow
                                                                                 status

  `GET`                   `/api/contract-review/{workflow_id}/report`            Get the generated
                                                                                 report

  `POST`                  `/api/contract-review/{workflow_id}/assign-reviewer`   Assign a reviewer

  `POST`                  `/api/contract-review/{workflow_id}/revise`            Submit revision
                                                                                 feedback

  `GET`                   `/api/contract-review/{workflow_id}/approve`           Approve the review
  ------------------------------------------------------------------------------------------------------

Interactive API documentation is available through FastAPI Swagger UI.

## Example: Start Contract Review

Request:

``` json
{
  "s3_paths": [
    "s3://ats/cvs/cv1.pdf",
    "s3://ats/cvs/cv2.pdf",
    "s3://ats/cvs/cv3.pdf"
  ],
  "job_id": "job-1d81f4b4-ee03-4fdf-a790-4f33ce76df37",
  "max_revisions": 2
}
```

Response:

``` json
{
  "workflow_id": "contract-review-66a83291-5316-4b5a-b5ee-654115aeb8a9"
}
```

The API returns the workflow ID immediately while the Temporal workflow
continues running in the background.

## Temporal

The system uses Temporal for workflow orchestration.

The main workflow is:

``` text
ContractReviewWorkflow
```

It creates multiple child workflows:

``` text
PDFSummaryWorkflow
```

Example Temporal execution:

``` text
ContractReviewWorkflow
├── PDFSummaryWorkflow (CV 1)
├── PDFSummaryWorkflow (CV 2)
└── PDFSummaryWorkflow (CV 3)
```

The Temporal Web UI can be used to monitor:

-   Workflow status
-   Child workflows
-   Event history
-   Pending activities
-   Workflow relationships
-   Workflow input
-   Workflow duration

A contract review remains `Running` while waiting for human review and
becomes `Completed` after approval.

## Storage

S3-compatible object storage is used for persistent files.

Example structure:

``` text
ats/
├── cvs/
│   ├── cv1.pdf
│   ├── cv2.pdf
│   └── cv3.pdf
│
└── jobs/
    ├── job-xxxx.txt
    └── job-yyyy.txt
```

The application uses environment variables for S3 configuration.

## Environment Variables

Create a `.env` file:

``` env
AWS_REGION=your-region
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_S3_ENDPOINT_URL=your-s3-endpoint

API_KEY=your-llm-api-key
MODEL_NAME=your-model-name
```

Do not commit `.env` or credentials to Git.

## Main Technologies

  Technology              Purpose
  ----------------------- ----------------------------------
  Python                  Application language
  FastAPI                 REST API
  Temporal                Workflow orchestration
  S3                      File and Job Description storage
  PyMuPDF                 PDF processing
  pymupdf4llm             PDF-to-Markdown extraction
  OpenAI-compatible API   LLM communication
  JSON Repair             Parsing structured LLM responses

## Running the Project

### 1. Install dependencies

Create and activate your Python environment, then install the project
dependencies.

``` bash
pip install -r requirements.txt
```

### 2. Configure environment variables

Create `.env` and configure the required S3 and LLM settings.

### 3. Start Temporal

Make sure a Temporal server is running and accessible.

### 4. Start the Temporal Worker

Start the worker responsible for the contract review and PDF processing
task queues.

### 5. Start FastAPI

Run the API application with Uvicorn.

``` bash
uvicorn <your_app_module>:<your_app> --reload
```

Replace `<your_app_module>` and `<your_app>` with the application's
actual module and FastAPI instance names.

### 6. Open Swagger UI

Open the FastAPI documentation in your browser:

``` text
http://localhost:8000/docs
```

## Example Processing Flow

``` text
1. Create Job Description
        │
        ▼
2. Receive job_id
        │
        ▼
3. Upload / reference candidate CVs
        │
        ▼
4. Start ContractReviewWorkflow
        │
        ▼
5. Create PDFSummaryWorkflow for each CV
        │
        ▼
6. Extract CV content
        │
        ▼
7. Analyze CV against Job Description
        │
        ▼
8. Generate ATS + Job Match Scores
        │
        ▼
9. Aggregate candidate results
        │
        ▼
10. Generate final report
        │
        ▼
11. Wait for human review
        │
        ├── Approve ──► Completed
        │
        └── Revise ──► LLM Revision ──► Review
```

## Project Status

This is an initial working implementation of an AI-powered ATS and
resume matching pipeline.

The current architecture focuses on:

-   Reliable workflow orchestration with Temporal.
-   Parallel CV processing.
-   Persistent object storage.
-   LLM-based candidate evaluation.
-   Human-in-the-loop review and revision.
