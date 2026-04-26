class Vehicle:
    def __init__(self, src, dest, path, roads, color):
        self.src = src
        self.dest = dest
        self.path = path
        self.edge_index = 0
        self.progress = 0.0
        self.time_alive = 0
        self.wait_time = 0
        self.color = color
        self.roads = roads

        u, v = path[0], path[1]
        self.roads[(u, v)].load += 1

    def update(self):
        self.progress += 0.03
        self.time_alive += 1

        u = self.path[self.edge_index]
        v = self.path[self.edge_index + 1]

        if self.roads[(u, v)].load > 3:
            self.wait_time += 1

        if self.progress >= 1:
            self.roads[(u, v)].load -= 1
            self.progress = 0
            self.edge_index += 1

            if not self.done():
                u = self.path[self.edge_index]
                v = self.path[self.edge_index + 1]
                self.roads[(u, v)].load += 1

    def done(self):
        return self.edge_index >= len(self.path) - 1

    def position(self, pos):
        if self.done():
            return None

        u = self.path[self.edge_index]
        v = self.path[self.edge_index + 1]

        x1, y1 = pos[u]
        x2, y2 = pos[v]

        return (
            x1 + (x2 - x1) * self.progress,
            y1 + (y2 - y1) * self.progress
        )