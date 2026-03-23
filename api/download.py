from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from metadata.database import SessionLocal
from metadata.models import Chunk, File as DBFile
from concurrent.futures import ThreadPoolExecutor
from config import MAX_RETRIES, TIMEOUT
import requests
import time
import logging
import os

logger = logging.getLogger(__name__)

router = APIRouter()                                                #Creates route group for download APIs


def is_node_healthy(node):
    try:
        response = requests.get(f"{node}/health", timeout=TIMEOUT)
        return response.status_code == 200
    except:
        return False


def fetch_chunk_data(chunk):
    nodes = chunk.nodes.split(",")

    healthy_nodes = [node for node in nodes if is_node_healthy(node)]

    if not healthy_nodes:
        logger.warning("All nodes marked unhealthy, falling back to all nodes")
        healthy_nodes = nodes

    # MAX_RETRIES = 3               Shifted to config file

    for node in healthy_nodes:
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.get(
                    f"{node}/get_chunk/{chunk.chunk_name}",
                    stream=True,
                    timeout=TIMEOUT
                )
                logger.info(f"Fetching chunk: {chunk.chunk_name}")

                if response.status_code == 200:
                    return response.content

            except Exception as e:
                logger.exception(f"Retry {attempt+1} failed for {node}: {e}")
            
            time.sleep(0.5 * (attempt + 1))

    return None


def delete_file(path: str):
    try:
        os.remove(path)
        print(f"Deleted temp file: {path}")
    except Exception as e:
        print(f"Error deleting file: {e}")


@router.get("/download")                                            #Define the endpoint
def download_file(file_id: str, background_tasks: BackgroundTasks): #file_id --> query parameter from URL, :str --> type hint (string) example request http://127.0.0.1:8000/download?file_id=129e5d9f...

    db = SessionLocal()

    #Checking if file exists 
    db_file = db.query(DBFile).filter(DBFile.id == file_id).first()
    if not db_file:
        db.close()
        raise HTTPException(status_code=404, detail="File not found")

    # chunks = sorted([                                               #returns the list of all files in folder
    #     f for f in os.listdir("storage_nodes")                      #This filters only files that belong to this file for example if file_id is abc then --> ["abc_chunk_0", "abc_chunk_1"]
    #     if f.startswith(file_id)
    # ])

    #Getting the chunks in order
    chunks = db.query(Chunk)\
        .filter(Chunk.file_id == file_id)\
        .order_by(Chunk.chunk_order)\
        .all()

    # if not chunks:                                                  #If no chunks are found then we return error message
    #     return {"error": "File not found"}

    #if chunks not found then we close the db and return error chunks not found
    if not chunks:
        db.close()
        raise HTTPException(status_code=404, detail="Chunks not found")


    output_file = f"temp/{file_id}_reconstructed"                   #Reconstructed file will be saved as temp/abc123_reconstructed

    # ✅ Fetch all chunks in parallel
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(fetch_chunk_data, chunks))      #Downloads multiple chunks at same time

    # ✅ Write chunks in order
    with open(output_file, "wb") as outfile:
        for i, data in enumerate(results):                      #Maintains correct file order
            if data is None:
                db.close()
                raise HTTPException(
                    status_code=500,
                    detail=f"Missing chunk: {chunks[i].chunk_name}"
                )

            outfile.write(data)
    db.close()

    background_tasks.add_task(delete_file, output_file)

    # Return reconstructed file
    return FileResponse(
        output_file,
        filename=db_file.name,
        media_type="application/octet-stream"
    )
    
   