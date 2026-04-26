import networkx as nx

class Router:
    def __init__(self, G):
        self.G = G

    def choose_path(self, src, dest):
        try:
            return nx.shortest_path(self.G, src, dest)
        except:
            return None