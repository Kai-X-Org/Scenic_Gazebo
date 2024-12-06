"""Newtonian simulator implementation."""

from cmath import atan, pi, tan
import math
from math import copysign, degrees, radians, sin
import os
import pathlib
import statistics
import time

from PIL import Image
import numpy as np

import scenic.core.errors as errors  # isort: skip

if errors.verbosityLevel == 0:  # suppress pygame advertisement at zero verbosity
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
# import pygame
# import shapely

from scenic.core.geometry import allChains, findMinMax
from scenic.core.regions import toPolygon
from scenic.core.simulators import SimulationCreationError
from scenic.core.vectors import Orientation, Vector
# from scenic.domains.driving.controllers import (
    # PIDLateralController,
    # PIDLongitudinalController,
# )
from scenic.syntax.veneer import verbosePrint

current_dir = pathlib.Path(__file__).parent.absolute()

WIDTH = 1280
HEIGHT = 800
MAX_ACCELERATION = 5.6  # in m/s2, seems to be a pretty reasonable value
MAX_BRAKING = 4.6

ROAD_COLOR = (0, 0, 0)
ROAD_WIDTH = 2
LANE_COLOR = (96, 96, 96)
CENTERLINE_COLOR = (224, 224, 224)
SIDEWALK_COLOR = (0, 128, 255)
SHOULDER_COLOR = (96, 96, 96)


class NewtonianSimulator(DrivingSimulator):
    """Implementation of `Simulator` for the Newtonian simulator.

    Args:
        network (Network): road network to display in the background, if any.
        render (bool): whether to render the simulation in a window.

    .. versionchanged:: 3.0

        The **timestep** argument is removed: it can be specified when calling
        `simulate` instead. The default timestep for the Newtonian simulator
        when not otherwise specified is still 0.1 seconds.
    """

    def __init__(self, network=None, render=False, debug_render=False, export_gif=False):
        super().__init__()
        self.export_gif = export_gif
        self.render = render
        self.debug_render = debug_render
        self.network = network

    def createSimulation(self, scene, **kwargs):
        simulation = NewtonianSimulation(
            scene, self.network, self.render, self.export_gif, self.debug_render, **kwargs
        )
        if self.export_gif and self.render:
            simulation.generate_gif("simulation.gif")
        return simulation


class NewtonianSimulation(DrivingSimulation):
    """Implementation of `Simulation` for the Newtonian simulator."""

    def __init__(
        self, scene, network, render, export_gif, debug_render, timestep, **kwargs
    ):
        self.render = render

        if timestep is None:
            timestep = 0.1

        super().__init__(scene, timestep=timestep, **kwargs)

    def setup(self):
        super().setup()

    def createObjectInSimulator(self, obj):
        # Set actor's initial speed
        pass


    def step(self):
        pass

    def getProperties(self, obj, properties):
        yaw, _, _ = obj.parentOrientation.globalToLocalAngles(obj.heading, 0, 0)

        values = dict(
            position=obj.position,
            yaw=yaw,
            pitch=0,
            roll=0,
            velocity=obj.velocity,
            speed=obj.speed,
            angularSpeed=obj.angularSpeed,
            angularVelocity=obj.angularVelocity,
        )
        if "elevation" in properties:
            values["elevation"] = obj.elevation
        return values

    def destroy(self):
        if self.render:
            pygame.quit()
