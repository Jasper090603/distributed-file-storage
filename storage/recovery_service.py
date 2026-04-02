import requests
import time
from metadata.database import SessionLocal
from metadata.models import Chunk
from config import NODES, REPLICATION_FACTOR


def get_alive_nodes():
    alive = []

    for node in NODES:
        try:
            res = requests.get(f"{node}/health", timeout=2)
            if res.status_code == 200:
                alive.append(node)
        except:
            continue

    return alive


def recover_chunks():
    db = SessionLocal()

    chunks = db.query(Chunk).all()
    alive_nodes = get_alive_nodes()

    print(f"[Recovery] Alive nodes: {alive_nodes}")

    for chunk in chunks:
        nodes = chunk.nodes.split(",")

        # only keep alive nodes
        active_nodes = [n for n in nodes if n in alive_nodes]

        if len(active_nodes) >= REPLICATION_FACTOR:
            continue  # healthy

        print(f"[Recovery] Fixing chunk: {chunk.chunk_name}")

        # pick source node (existing one)
        if not active_nodes:
            print(f"[Recovery] No replicas left for {chunk.chunk_name}")
            continue

        source_node = active_nodes[0]

        # fetch chunk from source
        try:
            response = requests.get(
                f"{source_node}/get_chunk/{chunk.chunk_name}",
                stream=True,
                timeout=5
            )

            if response.status_code != 200:
                continue

            chunk_data = response.content

        except:
            continue

        # find new nodes to replicate
        for node in alive_nodes:
            if node not in active_nodes:
                try:
                    files = {"file": (chunk.chunk_name, chunk_data)}
                    res = requests.post(f"{node}/store_chunk", files=files)

                    if res.status_code == 200:
                        active_nodes.append(node)
                        print(f"[Recovery] Replicated {chunk.chunk_name} to {node}")

                except:
                    continue

            if len(active_nodes) >= REPLICATION_FACTOR:
                break

        # update DB
        chunk.nodes = ",".join(active_nodes)

    db.commit()
    db.close()