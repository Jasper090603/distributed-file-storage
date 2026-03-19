import os
import uuid

CHUNK_SIZE = 10 * 1024 * 1024           #create a chunk size of 10MB ie 1024kb * 1024mb *10 = 10MB so that each file is split into 10MB chunks

def split_file(file_path):              #we create a function definition which takes file_path as parameter
    file_id = str(uuid.uuid4())         #Generating a unique file ID uuid.uuid4() generates a random unique file id and then str converts it into string
    chunks = []                         #Initializing chunks list

    with open (file_path, "rb") as f:   #opening the file in binary mode "rb" mean read binary opens the file in binary mode, with → context manager (auto closes file)
        chunk_number = 0                #Initializing the chunk counter keeps track of the chunk index
        
        while True:                     #Loop runs till be manually break it
            chunk = f.read(CHUNK_SIZE)  #Reads 10MB chunk from the file

            if not chunk:               #end condition is, if it is not a chunk then break that means we are at the end of the file
                break

            chunk_name = f"{file_id}_chunk_{chunk_number}"      # we create the chunk name with file id and chunk number ex. abc123_chunk_0
            chunk_path = f"storage_nodes/{chunk_name}"          #Define the path of the chunk which is stored in storage_nodes/{chunk_name}

            with open(chunk_path, "wb") as chunk_file:          #Write the chunk to disk where "wb" is write binary which writes the chunk data into a file
                chunk_file.write(chunk)


            chunks.append(chunk_name)                           #Adding chunk name to the list
            chunk_number += 1                                   #Increment the chunk counter

    return file_id, chunks                                      #Then at the end return the file_id and chunk list, this will be used as the metadata to reconstruct the file later