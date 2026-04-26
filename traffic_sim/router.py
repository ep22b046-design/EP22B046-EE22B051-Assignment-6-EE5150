import heapq

class Network:
    def __init__(self):
        self.nodes = {}
        self.edges = {}
        self.generators = {}
        self.collectors = {}

    # -------------------- add elements --------------------

    def add_junction(self, junc):
        self.nodes[junc.jid] = junc

    def add_road(self, rd):
        self.edges[rd.rid] = rd
        self.nodes[rd.j_from].add_outgoing(rd)
        self.nodes[rd.j_to].add_incoming(rd)

    def add_source(self, src):
        self.generators[src.node_id] = src

    def add_sink(self, snk):
        self.collectors[snk.node_id] = snk

    # -------------------- path interfaces --------------------

    def shortest_path(self, start, end):
        return self._compute_path(start, end, weight_factor=0.0)

    def congestion_aware_path(self, start, end, weight_factor=3.0):
        return self._compute_path(start, end, weight_factor=weight_factor)

    # -------------------- core algorithm --------------------

    def _compute_path(self, start, end, weight_factor=0.0):
        dist_map = {nid: float('inf') for nid in self.nodes}
        parent   = {nid: None for nid in self.nodes}

        dist_map[start] = 0
        heap = [(0, start)]

        while heap:
            cur_dist, u = heapq.heappop(heap)

            if cur_dist > dist_map[u]:
                continue

            for edge in self.nodes[u].out_roads:
                v = edge.j_to

                cost = edge.length * (1.0 + weight_factor * edge.occupancy)
                new_dist = cur_dist + cost

                if new_dist < dist_map[v]:
                    dist_map[v] = new_dist
                    parent[v] = u
                    heapq.heappush(heap, (new_dist, v))

        if dist_map[end] == float('inf'):
            return []

        # reconstruct path
        rev_path = []
        cur = end
        while cur is not None:
            rev_path.append(cur)
            cur = parent[cur]

        return list(reversed(rev_path))