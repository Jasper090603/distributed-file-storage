from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from metadata.database import SessionLocal
from metadata.models import Chunk, File as DBFile
import os

router = APIRouter()                                                #Creates route group for download APIs

@router.get("/download")                                            #Define the endpoint
def download_file(file_id: str):                                    #file_id --> query parameter from URL, :str --> type hint (string) example request http://127.0.0.1:8000/download?file_id=129e5d9f...

    os.makedirs("temp", exist_ok=True)

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

    with open(output_file, "wb") as outfile:                        #Opening the output file
        for chunk in chunks:                                        #Looping through the chunks
            # chunk_path = os.path.join(chunk.node, chunk.chunk_name) #Open chunk file in binary read mode
            nodes = chunk.nodes.split(",")

            chunk_found = False

            for node in nodes:
                chunk_path = os.path.join(node, chunk.chunk_name)

                if os.path.exists(chunk_path):                        #Merging the chunks, all chunks will be combined and original file will be restored
                    with open(chunk_path, "rb") as infile:
                        outfile.write(infile.read())
                    chunk_found = True
                    break
                   

            if not chunk_found:
                raise HTTPException(status_code=500, detail=f"Missing chunk: {chunk.chunk_name}")
                return {"error": f"Chunk missing: {chunk.chunk_name}"} 

    db.close()
    
    return FileResponse(output_file, filename=db_file.name)    #At the end return the output file