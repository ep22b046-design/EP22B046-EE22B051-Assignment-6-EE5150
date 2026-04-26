class Vehicle:
    def __init__(self, vid, src, dst, color='gray'):
        self.id = vid
        self.src = src
        self.dst = dst
        self.color = color

        self.path_plan = []
        self.active_road = None
        self.alpha = 0.0

        self.finished = False
        self.t_start = None
        self.t_end = None

        self.delay = 0.0
        self.free_flow_time = 0.0
        self.stop_count = 0


class Road:
    def __init__(self, rid, j_from, j_to, capacity=5, length=1.0):
        self.rid = rid
        self.j_from = j_from
        self.j_to = j_to

        self.capacity = capacity
        self.length = length

        self.on_road = []
        self.waiting = []

    @property
    def is_full(self):
        return len(self.on_road) >= self.capacity

    @property
    def occupancy(self):
        return len(self.on_road) / self.capacity if self.capacity > 0 else 0


class Junction:
    VALID_TYPES = {'2-way', '3-way', '4-way', 'source', 'sink', 'intersection'}

    def __init__(self, jid, jtype='intersection', x=0.0, y=0.0):
        assert jtype in self.VALID_TYPES

        self.jid = jid
        self.jtype = jtype
        self.x = x
        self.y = y

        self.in_roads = []
        self.out_roads = []

        self._rr_cursor = 0

    def add_incoming(self, road):
        self.in_roads.append(road)

    def add_outgoing(self, road):
        self.out_roads.append(road)

    def get_road_to(self, next_junction):
        for r in self.out_roads:
            if r.j_to == next_junction:
                return r
        return None

    def next_active_road(self):
        active = [r for r in self.in_roads if r.waiting]
        if not active:
            return None

        self._rr_cursor %= len(active)
        chosen = active[self._rr_cursor]
        self._rr_cursor = (self._rr_cursor + 1) % len(active)

        return chosen