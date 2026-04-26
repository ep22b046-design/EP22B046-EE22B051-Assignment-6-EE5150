class Collector:
    """Receives vehicles that have completed their journey."""

    def __init__(self, cid, node_id):
        self.cid = cid
        self.node_id = node_id
        self.completed = []

    def receive(self, veh, t_now):
        veh.finished = True
        veh.t_end = t_now
        self.completed.append(veh)