import numpy as np

class FlowGenerator:
    """Produces vehicles at a node using either Poisson or fixed-rate generation."""

    def __init__(self, sid, node_id, targets, intensity=0.3, pattern='poisson'):
        self.sid = sid
        self.node_id = node_id
        self.targets = targets          # list of destination node IDs
        self.intensity = intensity      # rate parameter
        self.pattern = pattern          # 'poisson' or 'constant'

    def spawn(self, t_now):
        """Returns a list of destination IDs for newly created vehicles."""
        if self.pattern == 'poisson':
            count = np.random.poisson(self.intensity)
        else:
            count = max(0, int(self.intensity))

        return [np.random.choice(self.targets) for _ in range(count)]