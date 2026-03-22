import os 
import random

NODES = ["storage_nodes/node1",
         "storage_nodes/node2",
         "storage_nodes/node3"]

def get_node_for_chunk():
    return random.choice(NODES)

def save_chunk(chunk_data, chunk_name):
    node = get_node_for_chunk()

    os.makedirs(node, exist_ok=True)

    chunk_path = os.path.join(node, chunk_name)

    with open(chunk_path, "wb") as f:
        f.write(chunk_data)

    return node, chunk_name