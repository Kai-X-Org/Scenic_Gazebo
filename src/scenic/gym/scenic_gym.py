from scenic.core.simulators import Simulator, Simulation
from scenic.core.scenarios import Scenario
import gymnasium as gym
from gymnasium import spaces
from typing import Callable

#TODO make ResetException
class ResetException(Exception):
    def __init__(self):
        super().__init__("Resetting")

class ScenicGymEnv(gym.Env):
    """
    verifai_sampler now not an argument added in here, but one specified int he Scenic program

    """
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4} # TODO placeholder, add simulator-specific entries
    
    def __init__(self, 
                 scenario : Scenario,
                 simulator_type : type, 
                 reward_fn : Callable,
                 render_mode=None, 
                 max_steps = 1000,
                 observation_space : spaces.Dict = spaces.Dict(),
                 action_space : spaces.Dict = spaces.Dict()): # empty string means just pure scenic???

        assert render_mode is None or render_mode in self.metadata["render_modes"]

        self.observation_space = observation_space
        self.action_space = action_space
        self.reward_fn = reward_fn
        self.render_mode = render_mode
        self.max_steps = max_steps
        self.simulator = simulator_type()

        self.simulation_results = []

        self.feedback_result = None
        self.loop = None

    def _make_run_loop(self):
        scene = self.scenario.generate(feedback=self.feedback_result)
        while True:
            try:
                with self.simulator.simulateStepped(scene, maxSteps=self.max_steps) as simulation:
                    # this first block before the while loop is for the first reset call
                    done = lambda: not (simulation.result is None)

                    simulation.advance()
                    observation = simulation.get_obs()
                    info = simulation.get_info() 

                    actions = yield observation, info
                    simulation.actions = actions # TODO add action dict to simulation interfaces

                    while not done():
                        # Probably good that we advance first before any action is set.
                        # this is consistent with how reset works
                        simulation.advance()
                        observation = self.get_obs()
                        info = self.get_info()
                        reward = self.reward_fn(observation) # will the reward_fn also be taking info as input, too?
                        actions = yield observation, reward, done(), info

                        if done():
                            self.feedback_result = simulation.result
                            self.simulation_results.append(simulation.result)
                            simulation.destroy()

                        simulation.actions = actions # TODO add action dict to simulation interfaces
                        
                        # TODO add some logic with regards to rendering, or do we need to?

            # except GeneratorExit: # maybe add a specific excpetion here
                # if not done():
                    # simulation.destroy()
                # raise StopIteration
                # # TODO should we do something right here?
            except ResetException:
                pass

    def reset(self, seed=None, options=None): # TODO will setting seed here conflict with VerifAI's setting of seed?
        # only setting enviornment seed, not torch seed?
        super().reset(seed=seed)
        if self.loop is None:
            self.loop = _make_run_loop()
        else:
            self.loop.throw(ResetException())

        # try:
            # self.loop.close()
        # except:
            # self.loop = self._make_run_loop()

        observation, info = next(self.loop) # not doing self.scene.send(action) just yet

        return observation, info
        
    def step(self, action):
        assert not (self.loop is None), "self.loop is None, have you called reset()?"

        observation, reward, done, info = self.loop.send(action)

    def render(): # TODO figure out if this function has to be implemented here or if super() has default implementation
        """
        likely just going to be something like simulation.render() or something
        """
        pass

    def close():
        self.simulator.destroy()

