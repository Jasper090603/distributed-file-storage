from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from metadata.database import SessionLocal
from metadata.models import Chunk, File as DBFile
from config import MAX_RETRIES, TIMEOUT
from concurrent.futures import ThreadPoolExecutor
import threading
import time
import requests
import time
import logging

logger = logging.getLogger(__name__)

router = APIRouter()                                                #Creates route group for download APIs


def is_node_healthy(node):
    try:
        response = requests.get(f"{node}/health", timeout=TIMEOUT)
        return response.status_code == 200
    except:
        return False


def stream_file_parallel(chunks):

    results = {}                 # buffer: {index: data}
    lock = threading.Lock()
    next_chunk = 0
    total_chunks = len(chunks)

    def fetch_chunk(index, chunk):
        nodes = chunk.nodes.split(",")

        for node in nodes:
            try:
                response = requests.get(
                    f"{node}/get_chunk/{chunk.chunk_name}",
                    stream=True,
                    timeout=5
                )

                if response.status_code == 200:
                    data = b''.join(response.iter_content(8192))

                    with lock:
                        results[index] = data
                    return

            except Exception as e:
                print(f"Fetch failed for {chunk.chunk_name} from {node}: {e}")
                continue

        # mark failure
        with lock:
            results[index] = None

    # Start parallel fetching
    with ThreadPoolExecutor(max_workers=5) as executor:
        for i, chunk in enumerate(chunks):
            executor.submit(fetch_chunk, i, chunk)

        # Streaming loop (ordered)
        while next_chunk < total_chunks:

            with lock:
                if next_chunk in results:
                    data = results.pop(next_chunk)

                    if data is None:
                        raise Exception(f"Missing chunk: {chunks[next_chunk].chunk_name}")

                    yield data
                    next_chunk += 1
                    continue

            time.sleep(0.01)  # wait for next chunk


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


@router.get("/download")                                            #Define the endpoint
def download_file(file_id: str, background_tasks: BackgroundTasks): #file_id --> query parameter from URL, :str --> type hint (string) example request http://127.0.0.1:8000/download?file_id=129e5d9f...

    db = SessionLocal()

    #Checking if file exists 
    db_file = db.query(DBFile).filter(DBFile.id == file_id).first()
    if not db_file:
        db.close()
        raise HTTPException(status_code=404, detail="File not found")

    #Getting the chunks in order
    chunks = db.query(Chunk)\
        .filter(Chunk.file_id == file_id)\
        .order_by(Chunk.chunk_order)\
        .all()


    #if chunks not found then we close the db and return error chunks not found
    if not chunks:
        db.close()
        raise HTTPException(status_code=404, detail="Chunks not found")


    return StreamingResponse(
        stream_file_parallel(chunks),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={db_file.name}"
        }
    )
    
   