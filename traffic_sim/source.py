import random
from .vehicle import Vehicle

class TrafficSource:
    def __init__(self, sources, sinks, router, roads, color_map):
        self.sources = sources
        self.sinks = sinks
        self.router = router
        self.roads = roads
        self.color_map = color_map

    def spawn(self):
        if random.random() < 0.15:
            src = random.choice(self.sources)
            dest = random.choice(self.sinks)

            if src == dest:
                return None

            path = self.router.choose_path(src, dest)
            if not path or len(path) < 2:
                return None

            return Vehicle(src, dest, path, self.roads, self.color_map[dest])

        return None