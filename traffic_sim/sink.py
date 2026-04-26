class Sink:
    def __init__(self):
        self.completed = 0
        self.total_time = 0
        self.total_wait = 0

    def collect(self, v):
        self.completed += 1
        self.total_time += v.time_alive
        self.total_wait += v.wait_time

    def stats(self):
        if self.completed == 0:
            return 0, 0
        return (
            self.total_time / self.completed,
            self.total_wait / self.completed
        )