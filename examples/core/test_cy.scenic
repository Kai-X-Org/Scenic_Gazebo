from scenic.simulators.metadrive.model import *
model scenic.domains.driing.model 

param map = localPath('../../assets/maps/CARLA/Town05.xodr')
param carla_map = 'Town05'
param time_step = 1.0/10

cy = CylinderRegion(dimensions=(1,1,1), position=(0,0,0))
# sph = SpheroidRegion(dimensions=(1,1,1), position=(0,0,0))

dim = 0.005

# obj = new Object in cy, with width 0.5, with height 0.5, with length 0.5
obj = new Car in cy
monitor TestIntersect():
    while True:
        wait
        print(cy.intersect(obj.occupiedSpace).size)
require monitor TestIntersect()
