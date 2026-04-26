# Traffic Network Simulator

A modular traffic simulation system for directed road networks with dynamic routing, congestion handling, and visualization.

---

## System Architecture

            +------------------+
            |     main.py      |
            | (network setup)  |
            +--------+---------+
                     |
                     v
      +-------------------------------+
      |        Simulation Engine      |
      | (time-step execution loop)    |
      +-------+----------+------------+
              |          |
              v          v
      +----------+   +-----------+
      |  Router  |   |  Sources  |
      | (paths)  |   | (spawn)   |
      +----------+   +-----------+
              |
              v
      +-----------------------+
      |  Components           |
      | (Vehicle, Road,       |
      |  Junction)            |
      +-----------------------+
              |
              v
        +-----------+
        |  Sinks    |
        | (exit)    |
        +-----------+

              |
              v
        +-----------+
        | Animator  |
        | (GIF)     |
        +-----------+

---

## Working Overview

The simulator models vehicle movement across a network of junctions connected by directed roads.

1. Network Setup  
   The topology (junctions and roads) is defined in main.py.

2. Vehicle Generation  
   Vehicles are generated at source nodes using constant rate or Poisson distribution.

3. Routing  
   Each vehicle computes a path using shortest-path logic.  
   Cost function used: cost = length * (1 + factor * occupancy)

4. Movement  
   Vehicles move continuously along roads, with position tracked as a fraction of road length.

5. Queueing  
   Vehicles wait at the end of roads if the next road is full. Each road maintains a queue.

6. Junction Processing  
   Junctions select which incoming road proceeds, while others accumulate delay.

7. Completion  
   Vehicles reach sinks and exit the network. Statistics are recorded.

---

## Modules

- components.py → Vehicle, Road, Junction definitions  
- source.py / sink.py → vehicle generation and exit  
- router.py → path computation (Dijkstra-style)  
- engine.py → simulation loop and metrics collection  
- anim.py → visualization (GIF)

---

## Statistics

Runtime (printed in terminal):

- Spawned → total vehicles generated  
- Arrived → vehicles reaching destination  
- Throughput → arrived / total_time  
- Average Travel Time → mean total time per vehicle  
- Average Delay → extra time due to congestion  
- Average Stops → number of halts per vehicle  

Animation overlay:

- Time → current simulation step  
- Moving → vehicles currently in motion  
- Queued → vehicles waiting  
- Arrived → completed vehicles  

---

## Output

Animation file: gifs/animation.gif

The animation shows node labels, congestion-colored roads, vehicle movement, queues, and live statistics.

---

## Run

python3 main.py
 
