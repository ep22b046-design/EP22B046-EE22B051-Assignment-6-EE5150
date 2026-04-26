import networkx as nx

class Router:
    def __init__(self, G, roads):
        self.G = G
        self.roads = roads

    def choose_path(self, src, dest):
        try:
            paths = list(nx.shortest_simple_paths(self.G, src, dest))[:3]
        except:
            return None

        best, best_cost = None, float('inf')

        for p in paths:
            cost = 0
            for i in range(len(p) - 1):
                e = (p[i], p[i + 1])
                cost += 1 + 4 * self.roads[e].load

            if cost < best_cost:
                best_cost = cost
                best = p

        return best