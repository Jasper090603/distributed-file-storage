from fastapi import FastAPI
from contextlib import asynccontextmanager
from metadata.database import engine, Base
from metadata import models 
from api import upload, download
from logger_config import setup_logger
from storage.recovery_service import recover_chunks
import threading
import logging
import time
import os


setup_logger()
logger = logging.getLogger(__name__)


app = FastAPI()

app.include_router(upload.router)
app.include_router(download.router)

def recovery_worker():
    while True:
        print("[Recovery] Running recovery cycle...")
        recover_chunks()
        time.sleep(10)  # run every 10 seconds

@app.on_event("startup")
def start_recovery():
    thread = threading.Thread(target=recovery_worker, daemon=True)
    thread.start()

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message:":"Distributed Drive Running"}