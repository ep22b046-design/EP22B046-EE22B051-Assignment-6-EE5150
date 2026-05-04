
import numpy as np
import math
from .components import Vehicle

def _rand_color():
    return "#{:06x}".format(np.random.randint(0, 0xFFFFFF))

class SimulationEngine:
    def __init__(self, network, steps=150, dt=1.0, speed=0.3, congestion_weight=3.0):
        self.net = network
        self.steps = steps
        self.dt = dt
        self.speed = speed
        self.weight = congestion_weight
        self.fleet = []
        self.time = 0.0
        self._vid = 0
        self.color_map = {d: _rand_color() for d in network.collectors.keys()}
        self.frames = []
        self.metrics = {
            'spawned': 0, 'arrived': 0, 'travel': [], 'delay': [],
            'freeflow': [], 'stops': [],
            'edge_load': {eid: [] for eid in network.edges},
            'edge_queue': {eid: [] for eid in network.edges},
            'node_delay': {nid: 0.0 for nid in network.nodes},
            'node_served': {nid: 0 for nid in network.nodes},
            'node_maxq': {nid: 0 for nid in network.nodes},
            'active': []
        }

    def _freeflow_time(self, path):
        total = 0.0
        for i in range(len(path) - 1):
            e = self.net.nodes[path[i]].get_road_to(path[i + 1])
            if e:
                total += e.length / self.speed
        return total

    def _spawn(self):
        for nid, gen in self.net.generators.items():
            for dest in gen.spawn(self.time):
                if dest == nid:
                    continue
                route = self.net.shortest_path(nid, dest)
                if len(route) < 2:
                    continue
                v = Vehicle(self._vid, nid, dest, self.color_map.get(dest, 'gray'))
                v.path_plan = route
                v.t_start = self.time
                v.free_flow_time = self._freeflow_time(route)
                v.stop_count = 0
                self._vid += 1
                self.metrics['spawned'] += 1
                first = self.net.nodes[route[0]].get_road_to(route[1])
                if first and not first.is_full:
                    first.on_road.append(v)
                    v.active_road = first.rid
                    v.alpha = 0.0
                    self.fleet.append(v)

    def _move(self):
        for v in self.fleet:
            if v.finished:
                continue
            edge = self.net.edges[v.active_road]
            v.alpha = min(1.0, v.alpha + self.speed / edge.length)
            if v.alpha >= 1.0 and v not in edge.waiting:
                edge.waiting.append(v)
                v.stop_count += 1

    def _process_nodes(self):
        for nid, node in self.net.nodes.items():
            total_q = sum(len(r.waiting) for r in node.in_roads)
            if total_q > self.metrics['node_maxq'][nid]:
                self.metrics['node_maxq'][nid] = total_q

            if nid in self.net.collectors:
                for r in node.in_roads:
                    for v in list(r.waiting):
                        r.waiting.remove(v)
                        r.on_road.remove(v)
                        self.net.collectors[nid].receive(v, self.time)
                        tt = self.time - v.t_start
                        self.metrics['travel'].append(tt)
                        self.metrics['delay'].append(v.delay)
                        self.metrics['freeflow'].append(v.free_flow_time)
                        self.metrics['stops'].append(v.stop_count)
                        self.metrics['arrived'] += 1
                continue

            road = node.next_active_road()
            if road is None or not road.waiting:
                for r in node.in_roads:
                    for v in r.waiting:
                        v.delay += self.dt
                        self.metrics['node_delay'][nid] += self.dt
                continue

            v = road.waiting[0]
            new_path = self.net.congestion_aware_path(nid, v.dst, self.weight)
            if new_path and len(new_path) >= 2:
                v.path_plan = new_path

            try:
                idx = v.path_plan.index(nid)
            except ValueError:
                road.waiting.pop(0)
                continue

            if idx + 1 >= len(v.path_plan):
                road.waiting.pop(0)
                road.on_road.remove(v)
                v.finished = True
                continue

            nxt = node.get_road_to(v.path_plan[idx + 1])
            if nxt and not nxt.is_full:
                road.waiting.remove(v)
                road.on_road.remove(v)
                nxt.on_road.append(v)
                v.active_road = nxt.rid
                v.alpha = 0.0
                self.metrics['node_served'][nid] += 1
            else:
                for r in node.in_roads:
                    for qv in r.waiting:
                        qv.delay += self.dt
                        self.metrics['node_delay'][nid] += self.dt

    def _record(self):
        state = {}
        for eid, edge in self.net.edges.items():
            qlen = len(edge.waiting)
            state[eid] = {
                'occupancy': edge.occupancy,
                'queue_len': qlen,
                'count': len(edge.on_road),
                'capacity': edge.capacity
            }
            self.metrics['edge_load'][eid].append(edge.occupancy)
            self.metrics['edge_queue'][eid].append(qlen)

        frame = {'time': self.time, 'vehicles': [], 'edges': state}

        # Offset distance for lane separation
        OFFSET = 0.15 

        for v in self.fleet:
            if v.finished:
                continue

            edge = self.net.edges[v.active_road]
            a = self.net.nodes[edge.j_from]
            b = self.net.nodes[edge.j_to]

            # Calculate direction vector and orthogonal vector
            dx = b.x - a.x
            dy = b.y - a.y
            length = math.hypot(dx, dy)
            
            if length > 0:
                nx = -dy / length  # Right-hand orthogonal x
                ny = dx / length   # Right-hand orthogonal y
            else:
                nx, ny = 0, 0

            # Apply orthogonal offset so vehicles sit in their respective lanes
            if v in edge.waiting:
                x = a.x + 0.9 * dx + nx * OFFSET
                y = a.y + 0.9 * dy + ny * OFFSET
                queued = True
            else:
                x = a.x + v.alpha * dx + nx * OFFSET
                y = a.y + v.alpha * dy + ny * OFFSET
                queued = False

            frame['vehicles'].append({
                'x': x,
                'y': y,
                'color': v.color,
                'dest': v.dst,
                'queued': queued
            })

        self.frames.append(frame)
        self.metrics['active'].append(len(frame['vehicles']))

    def run(self):
        print(f"Running simulation ({self.steps} steps)")
        for step in range(self.steps):
            self.time = step * self.dt
            self._spawn()
            self._move()
            self._process_nodes()
            self._record()
            if step % 20 == 0:
                print(f"Step {step:3d} | Active {self.metrics['active'][-1]} | Arrived {self.metrics['arrived']}")
        print(f"Done. Spawned={self.metrics['spawned']} Arrived={self.metrics['arrived']}")
        return self.metrics
