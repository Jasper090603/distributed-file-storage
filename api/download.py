from fastapi import APIRouter
from fastapi.responses import FileResponse
import os

router = APIRouter()                                                #Creates route group for download APIs

@router.get("/download")                                            #Define the endpoint
def download_file(file_id: str):                                    #file_id --> query parameter from URL, :str --> type hint (string) example request http://127.0.0.1:8000/download?file_id=129e5d9f...

    os.makedirs("temp", exist_ok=True)

    chunks = sorted([                                               #returns the list of all files in folder
        f for f in os.listdir("storage_nodes")                      #This filters only files that belong to this file for example if file_id is abc then --> ["abc_chunk_0", "abc_chunk_1"]
        if f.startswith(file_id)
    ])

    if not chunks:                                                  #If no chunks are found then we return error message
        return {"error": "File not found"}

    output_file = f"temp/{file_id}_reconstructed"                   #Reconstructed file will be saved as temp/abc123_reconstructed

    with open(output_file, "wb") as outfile:                        #Opening the output file
        for chunk in chunks:                                        #Looping through the chunks
            with open(f"storage_nodes/{chunk}", "rb") as infile:    #Open chunk file in binary read mode
                outfile.write(infile.read())                        #Merging the chunks, all chunks will be combined and original file will be restored

    return FileResponse(output_file, filename="downloaded_file")    #At the end return the output file