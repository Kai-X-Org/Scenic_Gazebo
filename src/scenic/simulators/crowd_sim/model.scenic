from scenic.simulators.crowd_sim.simulator import CrowdSimSimulator, CrowdSimSimulation

simulator CrowdSimSimulator()


class Agent:
    name: "agent"
    object_type: "agent"
    radius: 1
    shape: CylinderShape(self.radius, self.radius, 1)
    yaw: 0
    goal: (0, 0, 0)


class Human(Agent):
    name: "human"
    object_type: "human"
    radius: Range(0.3, 0.5)
    v_pref: Range(5, 1.5)

class Robot(Agent):
    name: "robot"
    object_type: "robot"
    radius: 1
