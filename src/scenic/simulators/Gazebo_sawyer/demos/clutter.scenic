model scenic.simulators.Gazebo_sawyer.model
from scenic.simulators.Gazebo_sawyer.model import *
from scenic.core.distributions import distributionFunction, RejectionException
from scenic.core.vectors import Vector
import trimesh
import math
import time

@distributionFunction
def clutterHelper(origin_pt, clutter) -> Vector:
    origin_pt = origin_pt.position
    top_surfaces = [c.topSurface.mesh for c in clutter]
    concat_surfaces = trimesh.util.concatenate(top_surfaces)
    intersection_data, _, _ = concat_surfaces.ray.intersects_location(
        ray_origins=[origin_pt],
        ray_directions=[[0,0,-1]],
        multiple_hits=False,
    )
    
    if len(intersection_data) == 0:
        raise RejectionException()

    # TODO UNPACK
    x, y, z = intersection_data[0][0], intersection_data[0][1], intersection_data[0][2]
    target_pt = Vector(x, y, z)
    print(f"target_point: {target_pt}")

    return target_pt

sampling_height = 20.0
sampling_radius = 0.5
sampling_space = SpheroidRegion(position=Vector(0, 0, sampling_height), 
                                dimensions=Vector(sampling_radius, sampling_radius, sampling_radius))

ego = new CafeTable on (0, 0, 0)
# hammer = new Hammer on ego
clutter_list = list()
for i in range(10):
    print('Num iter:', i)
    point = new Point in sampling_space
    new_cube = new WoodCube5cm on clutterHelper(point, clutter_list + [ego]), with yaw Range(0, 360) deg
    clutter_list.append(new_cube)
    point = new Point in sampling_space
    new_cube = new WoodCube10cm on clutterHelper(point, clutter_list + [ego]),with yaw Range(0, 360) deg
    clutter_list.append(new_cube)


