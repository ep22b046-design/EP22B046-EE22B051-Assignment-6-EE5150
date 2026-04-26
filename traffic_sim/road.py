class Road:
    def __init__(self, u, v, capacity=10):
        self.u = u
        self.v = v
        self.capacity = capacity
        self.load = 0