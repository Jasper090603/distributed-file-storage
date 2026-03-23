import os 
import random
import requests
from config import NODES, REPLICATION_FACTOR
import logging

logger = logging.getLogger(__name__)

# NODES = [                             Shifted to config.py file
#     "http://localhost:8001",
#     "http://localhost:8002",
#     "http://localhost:8003"
#          ]

# REPLICATION_FACTOR = 2                Shifted to config.py file

def get_nodes_for_replication():
    return random.sample(NODES, REPLICATION_FACTOR)

def save_chunk(chunk_data, chunk_name):
    selected_nodes = get_nodes_for_replication()

    for node in selected_nodes:

        files = {"file": (chunk_name, chunk_data)}

        response = requests.post(f"{node}/store_chunk", files=files)

        if response.status_code != 200:
            logger.error(f"Failed to store chunk in {node}")

        # chunk_path = os.path.join(node, chunk_name)

        # with open(chunk_path, "wb") as f:
        #     f.write(chunk_data)

    
    return selected_nodes, chunk_name