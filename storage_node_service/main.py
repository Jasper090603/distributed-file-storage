from fastapi import FastAPI, UploadFile, HTTPException, File
from fastapi.responses import FileResponse
import os
import shutil
import logging

logger = logging.getLogger(__name__)

app = FastAPI()

STORAGE_PATH = "data"

os.makedirs(STORAGE_PATH, exist_ok=True)

@app.post("/store_chunk")
async def store_chunk(file: UploadFile = File(...)):
    file_path = os.path.join(STORAGE_PATH, file.filename)

    logger.info(f"Storing chunk: {file.filename}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"message": "Chunk stored", "file": file.filename}

@app.get("/get_chunk/{chunk_name}")
def get_chunk(chunk_name: str):
    file_path = os.path.join(STORAGE_PATH, chunk_name)

    if not os.path.exists(file_path):
        logger.error(f"Chunk not found: {chunk_name}")
        raise HTTPException(status_code=404, detail="Chunk not found")

    logger.info(f"Serving chunk: {chunk_name}")
    
    return FileResponse(
        path=file_path,
        filename=chunk_name,
        media_type="application/octet-stream"
    )


@app.get("/health")
def health():
    return {"status": "ok"}