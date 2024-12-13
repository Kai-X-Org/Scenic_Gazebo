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
from scenic.core.simulators import Simulation, SimulationCreationError, Simulator
from scenic.core.vectors import Orientation, Vector
# from scenic.domains.driving.controllers import (
    # PIDLateralController,
    # PIDLongitudinalController,
# )
from scenic.syntax.veneer import verbosePrint
import matplotlib.pyplot as plt

current_dir = pathlib.Path(__file__).parent.absolute()


class CrowdSimSimulationCreationError(SimulationCreationError):
    def __init__(self, msg):
        self.msg = msg
        super().__init__(self.msg)

class CrowdSimSimulator(Simulator):
    """
    """

    def __init__(self, render=False, record="", timestep=0.1):
        super().__init__()
        self.timestep = timestep
        self.render = render
        self.config = ConfigNoArgs() # FIXME still need to import these
        self.env = CrowdSimPredRealGSTScenic()
        self.env.configure(self.config)

        fig, ax = plt.subplots(figsize=(7, 7))
        ax.set_xlim(-10, 10) # 6
        ax.set_ylim(-10, 10)
        ax.set_xlabel('x(m)', fontsize=16)
        ax.set_ylabel('y(m)', fontsize=16)
        plt.ion()
        plt.show()

        self.env.render_axis = ax
        

    def createSimulation(self, scene, **kwargs):
        simulation = CrowdSimSimulation(
            scene, self.env, self.render, self.record, timestep=self.timestep, **kwargs
        )
        if self.export_gif and self.render:
            simulation.generate_gif("simulation.gif")
        return simulation


class CrowdSimSimulation(Simulation):
    """Implementation of `Simulation` for the Newtonian simulator."""

    def __init__(
        self, scene, env, render, record timestep=0.1, **kwargs
    ):
        self.render = render
        self.record = record
        self.timestep = timestep
        self.env = env
        self.observation = None
        self.info = None
        self.reward = 0 # is this really the best value???

        self.actions = None # the step_action dictionary..though could change depending on space
        self.agent_params = dict()
        # self.human_dict = dict()

        if timestep is None:
            timestep = 0.1

        super().__init__(scene, timestep=timestep, **kwargs)

    def setup(self):
        # self.env.reset() # FIXME figure out where this should be called
        super().setup()
        self.env.reset()
        self.human_dict = self.env.human_dict


    def createObjectInSimulator(self, obj):
        # Set actor's initial speed
        px, py, _ = obj.position
        gx, gy, _ = obj.goal

        if obj.object_type == "robot":
            obj._sim_obj = self.env.robot # This should be fine
            # self.env.robot.set(px, py, gx, gy, 0, 0, obj.yaw) #TODO, what about the radius and v_pref arguments?
            self.agent_params["robot"] = dict(px=px,
                                              py=py,
                                              gx=gx,
                                              gy=gy)

        elif obj.object_type == "human":
            # obj._sim_obj = self.env.generate_circle_crossing_human_scenic(px, py)
            self.agent_params[obj.name] = dict(px=px,
                                              py=py,
                                              gx=-px,
                                              gy=-py)

        else:
            raise CrowdSimSimulationCreationError("Unrecognized object type during createObjectInSimulation")


    def step(self):
        #FIXME ensure type of self.actions match the expectation of self.env.step
        self.observation, self.reward, self.done, self.info = self.env.step(self.actions)
        self.actions = dict()

        if self.render:
            self.env.render()


    def getProperties(self, obj, properties):
        # yaw, _, _ = obj.parentOrientation.globalToLocalAngles(obj.heading, 0, 0)
        if obj.object_type == "robot":
            sim_obj = self.env.robot
        else:
            sim_obj = self.env.human_dict[obj.name]

        state = sim_obj.get_observable_state_list()
        position = Vecotr(state[0], state[1], 0)
        yaw = state[-1]
        velocity = Vector(state[2], state[3], 0)
            
        values = dict(
            position=position,
            yaw=yaw,
            pitch=0,
            roll=0,
            velocity=velocity,
            speed=velocity.norm(),
            angularSpeed=0,
            angularVelocity=0,
        )
        # if "elevation" in properties:
            # values["elevation"] = obj.elevation
        return values

    def get_obs(self):
        return self.observation

    def get_info(self):
        return self.info

    def destroy(self):
        # FIXME figure out how crowd_sim destroys...if at all
        super().destroy()
