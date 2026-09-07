from fastapi import FastAPI, APIRouter, Depends
import os
from time import sleep
from dotenv import load_dotenv
import logging
logger = logging.getLogger('uvicorn.error')

load_dotenv()

base_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"],
)
APP_NAME = os.environ['APP_NAME']
APP_VERSION = os.environ['APP_VERSION']

@base_router.get("/")
async def welcome():

    app_name = APP_NAME
    app_version = APP_VERSION

    return {
        "app_name": app_name,
        "app_version": app_version,
    }


    