import matplotlib.pyplot as plt
import matplotlib.animation as animation
import networkx as nx

from traffic_sim.road import Road
from traffic_sim.router import Router
from traffic_sim.source import TrafficSource
from traffic_sim.sink import Sink
from traffic_sim.engine import SimulationEngine

# graph of road network
pos = {
    0:(0,0),
    1:(2,3), 2:(4,3), 3:(6,3),
    4:(2,0), 5:(4,0), 6:(6,0),
    7:(2,-3), 8:(4,-3), 9:(6,-3),
    10:(8,0)
}

edges = [
    (0,1),(1,2),(2,3),(3,10),
    (0,4),(4,5),(5,6),(6,10),
    (0,7),(7,8),(8,9),(9,10),
    (1,4),(4,7),(2,5),(5,8),(3,6),(6,9),
    (1,5),(2,6),(4,8),(5,9)
]

edges = edges + [(v,u) for (u,v) in edges]

G = nx.DiGraph()
G.add_edges_from(edges)

nodes = list(pos.keys())

roads = {(u,v): Road(u,v) for (u,v) in edges}

color_map = {n: plt.cm.tab10(n % 10) for n in nodes}

sources = nodes[:4]
sinks = nodes[-4:]

router = Router(G, roads)
source = TrafficSource(sources, sinks, router, roads, color_map)
sink = Sink()

engine = SimulationEngine(roads, source, sink)

#anim
fig, ax = plt.subplots()

def animate(frame):
    engine.step()
    ax.clear()

    avg_time, avg_wait = sink.stats()

    ax.set_title(
        f"Active: {len(engine.vehicles)} | Done: {sink.completed} | AvgTime: {avg_time:.1f} | AvgWait: {avg_wait:.1f}"
    )

    for (u,v),r in roads.items():
        x1,y1 = pos[u]
        x2,y2 = pos[v]
        ax.plot([x1,x2],[y1,y2],'black',alpha=0.2)

    for v in engine.vehicles:
        p = v.position(pos)
        if p:
            ax.scatter(p[0], p[1], color=v.color, s=60)

    for n,(x,y) in pos.items():
        ax.scatter(x,y,color='white',edgecolors='black',s=300)
        ax.text(x,y,str(n),ha='center',va='center')

    ax.axis('off')

ani = animation.FuncAnimation(fig, animate, interval=60)
plt.show()

print("\nFINAL STATS")
print("Throughput:", sink.completed)