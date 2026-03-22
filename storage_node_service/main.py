from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import os
import shutil

app = FastAPI()

STORAGE_PATH = "data"

os.makedirs(STORAGE_PATH, exist_ok=True)

@app.post("/store_chunk")
async def store_chunk(file: UploadFile = File(...)):
    file_path = os.path.join(STORAGE_PATH, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"message": "Chunk stored", "file": file.filename}

@app.get("/get_chunk/{chunk_name}")
def get_chunk(chunk_name: str):
    file_path = os.path.join(STORAGE_PATH, chunk_name)

    if not os.path.exists(file_path):
        return {"error": "Chunk not found"}

    return FileResponse(file_path, media_type="application/octet-stream")