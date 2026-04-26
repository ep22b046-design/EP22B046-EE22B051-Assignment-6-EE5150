class Junction:
    def __init__(self, node_id, max_throughput=1):
        self.id = node_id
        self.queue = []
        self.max_throughput = max_throughput

    def arrive(self, vehicle):
        self.queue.append(vehicle)

    def step(self, roads):
        moved = 0
        for v in list(self.queue):
            if moved >= self.max_throughput:
                break

            if v.done():
                continue

            u = v.path[v.edge_index]
            w = v.path[v.edge_index + 1]
            road = roads[(u, w)]

            if road.can_enter():
                road.enter(v)
                v.on_road = True
                v.progress = 0
                self.queue.remove(v)
                moved += 1