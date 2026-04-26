import numpy as np

np.random.seed(42)

from traffic_sim.components import Road, Junction
from traffic_sim.source import FlowGenerator
from traffic_sim.sink import Collector
from traffic_sim.router import Network
from traffic_sim.engine import SimulationEngine
from traffic_sim.anim import SimulationAnimator


SIM_STEPS   = 150
TIME_STEP   = 1.0
SPEED       = 0.18

GEN_RATE    = 0.4
GEN_MODE    = 'poisson'

ROUTE_WEIGHT = 3.0


def create_topology():

    net = Network()

    node_data = [
        (0, 'source', 0, 3),
        (1, 'intersection', 2, 5),
        (2, 'intersection', 2, 1),
        (3, 'intersection', 4, 6),
        (4, 'intersection', 4, 3),
        (5, 'intersection', 6, 4),
        (6, 'sink', 8, 6),
        (7, 'sink', 8, 2),
    ]

    for nid, kind, x, y in node_data:
        net.add_junction(Junction(nid, kind, x, y))

    edge_data = [
        ('A', 0, 1, 5, 2.5),
        ('B', 0, 2, 5, 2.5),
        ('C', 1, 3, 4, 2.0),
        ('D', 2, 4, 4, 2.0),
        ('E', 3, 6, 5, 3.0),
        ('F', 4, 5, 5, 2.5),
        ('G', 5, 6, 5, 2.5),
        ('H', 5, 7, 5, 2.5),
        ('I', 1, 4, 3, 3.2),
    ]

    for eid, a, b, cap, length in edge_data:
        net.add_road(Road(eid, a, b, cap, length))

    net.add_source(
        FlowGenerator(
            sid='GEN0',
            node_id=0,
            targets=[6, 7],
            intensity=GEN_RATE,
            pattern=GEN_MODE
        )
    )

    net.add_sink(Collector('END6', 6))
    net.add_sink(Collector('END7', 7))

    return net


if __name__ == "__main__":

    net = create_topology()

    engine = SimulationEngine(
        net,
        steps=SIM_STEPS,
        dt=TIME_STEP,
        speed=SPEED,
        congestion_weight=ROUTE_WEIGHT
    )

    engine.run()

    viz = SimulationAnimator(
        net,
        engine.frames,
        engine.metrics,
        engine.color_map
    )

    viz.animate(out='output/simulation.gif', fps=10, step=2)

    print("\nOutputs saved in 'output/' directory")