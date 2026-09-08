import os

from dotenv import load_dotenv
from temporalio.client import Client


load_dotenv()

TEMPORAL_HOST = os.environ["TEMPORAL_HOST"]
TEMPORAL_NAMESPACE = os.environ["TEMPORAL_NAMESPACE"]
TEMPORAL_CONTRACT_REVIEW_TASK_QUEUE = os.environ['TEMPORAL_CONTRACT_REVIEW_TASK_QUEUE']


async def get_temporal_client() -> Client:
    return await Client.connect(
        TEMPORAL_HOST,
        namespace=TEMPORAL_NAMESPACE,
    )