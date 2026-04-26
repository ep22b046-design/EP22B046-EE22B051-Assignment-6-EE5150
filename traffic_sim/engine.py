class SimulationEngine:
    def __init__(self, roads, source, sink):
        self.roads = roads
        self.source = source
        self.sink = sink
        self.vehicles = []
        self.tick = 0

    def step(self):
        self.tick += 1

        new_vehicle = self.source.spawn()
        if new_vehicle:
            self.vehicles.append(new_vehicle)

        new_list = []
        for v in self.vehicles:
            v.update()

            if v.done():
                self.sink.collect(v)
            else:
                new_list.append(v)

        self.vehicles = new_list