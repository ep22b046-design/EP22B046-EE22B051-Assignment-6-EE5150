
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.colors import LinearSegmentedColormap
import os
import math

os.makedirs("output", exist_ok=True)

FLOW_MAP = LinearSegmentedColormap.from_list(
    'flow_map', ['#2ecc71', '#f1c40f', '#e74c3c'], N=256
)

def _edge_color(v):
    return FLOW_MAP(min(float(v), 1.0))

class SimulationAnimator:
    def __init__(self, net, frames, metrics, color_map):
        self.net = net
        self.frames = frames
        self.metrics = metrics
        self.color_map = color_map

    def _draw_nodes(self, ax):
        for n in self.net.nodes.values():
            if n.jid in self.net.collectors:
                col = '#ff6b6b'
                label = f'J{n.jid}\nSink'
            elif n.jid in self.net.generators:
                col = '#51cf66'
                label = f'J{n.jid}\nSrc'
            else:
                col = '#4dabf7'
                label = f'J{n.jid}'

            circ = plt.Circle((n.x, n.y), 0.35,
                              color=col, ec='black', lw=1.2, zorder=5)
            ax.add_patch(circ)

            ax.text(n.x, n.y, label,
                    color='black', fontsize=7,
                    ha='center', va='center',
                    fontweight='bold',
                    zorder=6)

    def animate(self, out='output/simulation.gif', fps=10, step=2):
        fig, ax = plt.subplots(figsize=(12, 9))
        fig.patch.set_facecolor('white')
        ax.set_facecolor('#f8f9fa')

        xs = [n.x for n in self.net.nodes.values()]
        ys = [n.y for n in self.net.nodes.values()]

        ax.set_xlim(min(xs)-1.5, max(xs)+1.5)
        ax.set_ylim(min(ys)-1.5, max(ys)+1.5)
        ax.set_aspect('equal')

        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

        self._draw_nodes(ax)

        frames = self.frames[::step]
        OFFSET = 0.15 # Must match engine for accurate vehicle tracking

        def update(frame):
            ax.cla()
            ax.set_facecolor('#f8f9fa')
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)

            self._draw_nodes(ax)

            edge_state = frame.get('edges', {})

            for e in self.net.edges.values():
                a = self.net.nodes[e.j_from]
                b = self.net.nodes[e.j_to]

                st = edge_state.get(e.rid, {})
                occ = st.get('occupancy', 0)
                ql = st.get('queue_len', 0)

                # Find direction
                dx = b.x - a.x
                dy = b.y - a.y
                length = math.hypot(dx, dy)

                if length == 0:
                    continue
                
                # Apply orthogonal offset
                nx = -dy / length
                ny = dx / length
                
                x1 = a.x + nx * OFFSET
                y1 = a.y + ny * OFFSET
                x2 = b.x + nx * OFFSET
                y2 = b.y + ny * OFFSET

                ax.plot([x1, x2], [y1, y2],
                        color=_edge_color(occ), lw=2, zorder=2)

                mx, my = (x1 + x2) / 2, (y1 + y2) / 2

                ax.text(mx, my,
                        f'{e.rid}\nQ:{ql}',
                        fontsize=6,
                        color='black',
                        ha='center', va='center',
                        bbox=dict(facecolor='white', alpha=0.6, edgecolor='none', pad=0.2),
                        zorder=3)

            # Draw vehicles
            mv = [v for v in frame['vehicles'] if not v['queued']]
            qv = [v for v in frame['vehicles'] if v['queued']]

            if mv:
                ax.scatter([v['x'] for v in mv],
                           [v['y'] for v in mv],
                           c=[v['color'] for v in mv],
                           s=40, edgecolors='black', zorder=4)

            if qv:
                ax.scatter([v['x'] for v in qv],
                           [v['y'] for v in qv],
                           c=[v['color'] for v in qv],
                           s=60, marker='s', edgecolors='black', zorder=4)

            ax.text(0.02, 0.97, f'Time: {frame["time"]:.0f}',
                    transform=ax.transAxes, fontsize=10)

            ax.text(0.02, 0.88,
                    f'Moving: {len(mv)}\nQueued: {len(qv)}\nArrived: {self.metrics["arrived"]}',
                    transform=ax.transAxes, fontsize=9)

            return []

        anim = FuncAnimation(fig, update, frames=frames, interval=120)
        anim.save(out, writer=PillowWriter(fps=fps))
        plt.close()

        print(f"Saved → {out}")
