import hashlib
import bisect


class ConsistentHashRing:
    def __init__(self, nodes, replicas=3):
        self.replicas = replicas
        self.ring = {}
        self.sorted_keys = []

        for node in nodes:
            self.add_node(node)

    def hash(self, key):
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def add_node(self, node):
        for i in range(self.replicas):
            virtual_node = f"{node}#{i}"
            key = self.hash(virtual_node)

            self.ring[key] = node
            self.sorted_keys.append(key)

        self.sorted_keys.sort()

    def get_nodes(self, key, num_replicas=2):
        hash_key = self.hash(key)

        idx = bisect.bisect(self.sorted_keys, hash_key)

        result = []
        visited = set()

        i = 0
        while len(result) < num_replicas and i < len(self.sorted_keys):
            index = (idx + i) % len(self.sorted_keys)
            node = self.ring[self.sorted_keys[index]]

            if node not in visited:
                result.append(node)
                visited.add(node)

            i += 1

        return result