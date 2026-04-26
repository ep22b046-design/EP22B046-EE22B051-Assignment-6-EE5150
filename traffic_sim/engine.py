class SimulationEngine:
    def __init__(self, roads, junctions, source, sink):
        self.roads = roads
        self.junctions = junctions
        self.source = source
        self.sink = sink
        self.vehicles = []
        self.tick = 0

    def step(self):
        self.tick += 1

        v = self.source.spawn()
        if v:
            self.junctions[v.src].arrive(v)
            self.vehicles.append(v)

        # move vehicles on roads
        for road in self.roads.values():
            for v in list(road.vehicles):
                v.progress += 0.04
                v.time_alive += 1

                if v.progress >= 1:
                    road.leave(v)
                    v.edge_index += 1

                    if v.done():
                        self.sink.collect(v)
                        self.vehicles.remove(v)
                    else:
                        self.junctions[v.path[v.edge_index]].arrive(v)
                        v.on_road = False

        # junctions
        for j in self.junctions.values():
            for v in j.queue:
                v.wait_time += 1
            j.step(self.roads)