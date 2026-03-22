import os 
import random

NODES = ["storage_nodes/node1",
         "storage_nodes/node2",
         "storage_nodes/node3"]

REPLICATION_FACTOR = 2

def get_nodes_for_replication():
    return random.sample(NODES, REPLICATION_FACTOR)

def save_chunk(chunk_data, chunk_name):
    selected_nodes = get_nodes_for_replication()

    for node in selected_nodes:

        os.makedirs(node, exist_ok=True)

        chunk_path = os.path.join(node, chunk_name)

        with open(chunk_path, "wb") as f:
            f.write(chunk_data)

    return selected_nodes, chunk_name