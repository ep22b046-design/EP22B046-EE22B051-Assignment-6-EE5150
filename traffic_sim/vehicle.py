class Vehicle:
    def __init__(self, src, dest, path, color):
        self.src = src
        self.dest = dest
        self.path = path
        self.edge_index = 0
        self.progress = 0
        self.time_alive = 0
        self.wait_time = 0
        self.color = color
        self.on_road = False

    def done(self):
        return self.edge_index >= len(self.path) - 1