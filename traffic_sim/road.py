class Road:
    def __init__(self, u, v, capacity=5):
        self.u = u
        self.v = v
        self.capacity = capacity
        self.vehicles = []

    def can_enter(self):
        return len(self.vehicles) < self.capacity

    def enter(self, vehicle):
        self.vehicles.append(vehicle)

    def leave(self, vehicle):
        if vehicle in self.vehicles:
            self.vehicles.remove(vehicle)