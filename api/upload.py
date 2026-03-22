from fastapi import APIRouter, HTTPException, UploadFile, File             #API Router used to create modular routes, #UploadFile Represents uploaded file, #File tells FastAPI this is a file input
import shutil                                               #shutil is used for file copying operations, efficient for handling large files
import os                                                   #Used to create folders and handling file paths
import uuid
from storage.chunker import split_file                      #Imports chunking function, connects APi --> storage logic
from metadata.database import SessionLocal
from metadata.models import File as DBFile, Chunk


router = APIRouter()                                        #Creates a route group helps organize endpoints like /upload /download /delete

TEMP_FOLDER = "temp"                                        #temporary storeage for uploaded files before processing

os.makedirs(TEMP_FOLDER, exist_ok = True)                   #Creates directory if doesn't exists prevents error if folder already exists
os.makedirs("storage_nodes", exist_ok = True)               

@router.post("/upload")                                     #This creates and HTTP POST endpoint, URL will be /upload, used for sending files to server

async def upload_file(file: UploadFile = File(...)):        #Asynchronous function allows to handle multiple requests efficiently  #file: UploadFile, parameter named file, type is UploadFile   #File(...), this tells FastAPI that this parameter is required and comes from a file upload, ... means required field
   try:

    unique_name = f"{uuid.uuid4()}_{file.filename}"         #Generate unique filename
    temp_path = os.path.join(TEMP_FOLDER, unique_name)      #Create temporary file path ex. file.filename = "photo.jpg" becomes: temp/photo.jpg
                                                           
    with open(temp_path, "wb") as buffer:                   #Saves the uploaded file "wb" write in binary mode, file.file is actual file stream(data sent by user), buffer is destination file on disk
        shutil.copyfileobj(file.file, buffer)               #shutil.copyfileobj(source, destination) copies file efficiently

    file_id, chunks = split_file(temp_path)                 #Calling the chunking function

    db = SessionLocal()

    db_file = DBFile(
       id = file_id,
       name = file.filename,
       size = os.path.getsize(temp_path)
    )

    db.add(db_file)
    db.commit()


    for chunk in chunks:
       db_chunk = Chunk(
          file_id = file_id,
          chunk_name = chunk["chunk_name"],
          chunk_order = chunk["order"],
          nodes = ",".join(chunk["nodes"])
       )
       db.add(db_chunk)

    db.commit()
    db.close()

    os.remove(temp_path)                                    #Delete temp file after chunking 

    return{                                                 #returns the response
        "file_id": file_id,
        "chunks": chunks
    }
   except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))