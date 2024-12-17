from scenic.simulators.crowd_sim.model import *
from scenic.simulators.crowd_sim.simulator import CrowdSimSimulator

param verifaiSamplerType = 'halton'
param x = VerifaiRange(-3, 3)
param y = VerifaiRange(-3, -1)
param gx = VerifaiRange(-3, 3)
param gy = VerifaiRange(3, 4)

# param hx1 = VerifaiRange(-3, 3)
# param hy1 = VerifaiRange()

simulator CrowdSimSimulator()


ego = new Robot at (globalParameters.x, globalParameters.y, 0), with yaw 0 deg, 
                    with goal (globalParameters.gx, globalParameters.gy, 0)

human1 = new Human at (globalParameters.x, 0, 0), 
                    with name "human1", with yaw 45 deg

human2 = new Human at (Range(0, 3), 0, 0), with name "human2", with yaw 45 deg

human3 = new Human at (3, 3, 0), with name "human3", with yaw 45 deg

# human4 = new Human at (-3, 3, 0), with name "human4", with yaw 45 deg

