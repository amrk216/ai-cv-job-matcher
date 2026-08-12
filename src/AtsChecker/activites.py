import os
import math
from pathlib import Path
import tempfile
from dataclasses import dataclass

import boto3
import fitz  #pyMuPDF  --page-by-page extraction

import pymupdf4llm
from dotenv import load_dotenv
from openai import OpenAI
from temporalio import activity

from DataClasses import ExtractPDFInput,ExtractPDFOutput,CallLLMInput,CallLLMOutput
from helpers import get_s3_path,parse_s3_path

#activity 1 : Extract pdf from s3 
@activity.defn
async def extract_pdf(params:ExtractPDFInput)-> ExtractPDFOutput:

    activity.logger.info(f"Starting ectraction:{ params.s3_path}")

    activity.heartbeat({
        "stage":"Downloding...",
        "s3_path":params.s3_path,
        "pages_done":0,
        "chars_exacted":0
    })

    # connection with s3
    s3_client = get_s3_path()

    bucket,key = parse_s3_path(params.s3_path)

    # download file in local machine
    filename = Path(key).name
    TEMP_DIR = os.environ['TEMP_DIR']

    local_path = str(Path(TEMP_DIR/filename))

    doc = fitz.open(local_path)
    total_pages = doc.page_count

    activity.logger.info(f"Download {total_pages} page pdf {params.s3_path}")

    all_text_chunks = []
    total_chars_num = 0
    num_batches = math.ceil(total_pages/params.batch_size)

    for batch_idx in range(num_batches):
        start_page =  batch_idx * params.batch_size
        end_page = min(start_page + params.batch_size,total_pages)

        batch_md = pymupdf4llm.to_markdown(
            local_path,
            pages = list(range(start_page,end_page))
        )
        all_text_chunks.append(batch_md)
        total_chars_num+=len(batch_md)

        activity.heartbeat({

            "stage" : "Extracting.....",
            "s3_path" : params.s3_path,
            "paged_done" : end_page,
            "total_pages": total_pages,
            "batch":         f'{start_page + 1}-{end_page}',
            "chars_extracted":total_chars_num,
            "progress_pct": round(end_page / total_pages *100),

        })

        full_md = "\n\n".join(all_text_chunks)

        activity.heartbeat({
        
                    "cvs" : "Done",
                    "s3_path" : params.s3_path,
                    "paged_done" : total_pages,
                    "total_pages": total_pages,    
                    "chars_extracted":total_chars_num,

                })

    return ExtractPDFOutput(
        s3_path=params.s3_path,
        markdown_text=full_md,
        page_count=total_pages
        )

# activite 2 : call llm
@activity.defn
async def call_llm(params:CallLLMInput)->CallLLMOutput:
    activity.info(f"Calling LLM")
    activity.heartbeat({
        "stage" : "Calling....",
        "prompt_chats": len(params.prompt)
    })


    llm_client = OpenAI(
        api_key= os.environ["API_KEY"],
        base_url="https://inference.dahl.global/v1"
    )

    response = llm_client.chat.completions.create(
        model = os.environ.get('MODEL_NAME'),
        messages = [{"role":"user","content":params.prompt}],
        max_tokens=1000
    )

    content = response.choices[0].message.content

    activity.logger.info(f'llm returned {len(content)} chars')

    return CallLLMOutput(
        content=content
    )
