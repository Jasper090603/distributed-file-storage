from fastapi import FastAPI
from contextlib import asynccontextmanager
from metadata.database import engine, Base
from metadata import models 
from api import upload, download


app = FastAPI()

app.include_router(upload.router)
app.include_router(download.router)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message:":"Distributed Drive Running"}