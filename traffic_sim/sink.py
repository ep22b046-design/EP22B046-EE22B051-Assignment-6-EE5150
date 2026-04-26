class Sink:
    def __init__(self):
        self.completed = 0
        self.total_time = 0
        self.total_wait = 0

    def collect(self, vehicle):
        self.completed += 1
        self.total_time += vehicle.time_alive
        self.total_wait += vehicle.wait_time

    def stats(self):
        if self.completed == 0:
            return 0, 0
        return (
            self.total_time / self.completed,
            self.total_wait / self.completed
        )