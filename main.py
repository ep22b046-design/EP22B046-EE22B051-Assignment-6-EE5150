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
        # Top row
        (0, 'source', 0, 5),        # Source S1, S4 (Top-Left)
        (1, 'intersection', 3, 5),  # Top-Left Junction
        (2, 'intersection', 6, 5),  # Top-Right Junction
        (3, 'sink', 9, 5),          # Sink K2 (Top-Right)

        # Middle row
        (4, 'source', 0, 3),        # Source S2, S5 (Mid-Left)
        (5, 'intersection', 3, 3),  # Mid-Left Junction
        (6, 'intersection', 6, 3),  # Mid-Right Junction
        (7, 'source', 9, 3),        # Source S3 (Mid-Right)

        # Bottom row
        (8, 'sink', 0, 1),          # Sink K3, K4 (Bottom-Left)
        (9, 'intersection', 3, 1),  # Bottom-Left Junction
        (10, 'intersection', 6, 1), # Bottom-Right Junction
        (11, 'sink', 9, 1),         # Sink K1, K5 (Bottom-Right)
    ]

    for nid, kind, x, y in node_data:
        net.add_junction(Junction(nid, kind, x, y))

    # Define edges (Bi-directional = 2 edges per road segment)
    # Format: (edge_id, from_node, to_node, capacity, length)
    CAP = 5     # Default capacity
    LEN_H = 3.0 # Horizontal road length
    LEN_V = 2.0 # Vertical road length

    edge_data = [
        # --- Top Row Horizontal ---
        ('E01_f', 0, 1, CAP, LEN_H), ('E01_b', 1, 0, CAP, LEN_H),
        ('E12_f', 1, 2, CAP, LEN_H), ('E12_b', 2, 1, CAP, LEN_H),
        ('E23_f', 2, 3, CAP, LEN_H), ('E23_b', 3, 2, CAP, LEN_H),

        # --- Middle Row Horizontal ---
        ('E45_f', 4, 5, CAP, LEN_H), ('E45_b', 5, 4, CAP, LEN_H),
        ('E56_f', 5, 6, CAP, LEN_H), ('E56_b', 6, 5, CAP, LEN_H),
        ('E67_f', 6, 7, CAP, LEN_H), ('E67_b', 7, 6, CAP, LEN_H),

        # --- Bottom Row Horizontal ---
        ('E89_f', 8, 9, CAP, LEN_H), ('E89_b', 9, 8, CAP, LEN_H),
        ('E910_f', 9, 10, CAP, LEN_H), ('E910_b', 10, 9, CAP, LEN_H),
        ('E1011_f', 10, 11, CAP, LEN_H), ('E1011_b', 11, 10, CAP, LEN_H),

        # --- Left Column Vertical ---
        ('E15_f', 1, 5, CAP, LEN_V), ('E15_b', 5, 1, CAP, LEN_V),
        ('E59_f', 5, 9, CAP, LEN_V), ('E59_b', 9, 5, CAP, LEN_V),

        # --- Right Column Vertical ---
        ('E26_f', 2, 6, CAP, LEN_V), ('E26_b', 6, 2, CAP, LEN_V),
        ('E610_f', 6, 10, CAP, LEN_V), ('E610_b', 10, 6, CAP, LEN_V),
    ]

    for eid, a, b, cap, length in edge_data:
        net.add_road(Road(eid, a, b, cap, length))

    all_sinks = [3, 8, 11]

    net.add_source(FlowGenerator(sid='GEN_S1_S4', node_id=0, targets=all_sinks, intensity=GEN_RATE, pattern=GEN_MODE))
    net.add_source(FlowGenerator(sid='GEN_S2_S5', node_id=4, targets=all_sinks, intensity=GEN_RATE, pattern=GEN_MODE))
    net.add_source(FlowGenerator(sid='GEN_S3',    node_id=7, targets=all_sinks, intensity=GEN_RATE, pattern=GEN_MODE))

    net.add_sink(Collector('SINK_K2', 3))
    net.add_sink(Collector('SINK_K3_K4', 8))
    net.add_sink(Collector('SINK_K1_K5', 11))

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
    # ===== FINAL STATISTICS =====
    m = engine.metrics

    avg_travel = np.mean(m['travel']) if m['travel'] else 0
    avg_delay  = np.mean(m['delay']) if m['delay'] else 0
    avg_stops  = np.mean(m['stops']) if m['stops'] else 0

    throughput = m['arrived'] / (SIM_STEPS * TIME_STEP)

    print("\n===== FINAL STATS =====")
    print(f"Spawned   : {m['spawned']}")
    print(f"Arrived   : {m['arrived']}")
    print(f"Throughput: {throughput:.3f} veh/step")
    print(f"Avg Travel: {avg_travel:.2f}")
    print(f"Avg Delay : {avg_delay:.2f}")
    print(f"Avg Stops : {avg_stops:.2f}")

    viz = SimulationAnimator(
        net,
        engine.frames,
        engine.metrics,
        engine.color_map
    )

    viz.animate(out='output/simulation.gif', fps=10, step=2)

    print("\nOutputs saved in 'output/' directory")
