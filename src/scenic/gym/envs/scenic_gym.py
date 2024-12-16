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
                 # simulator_type : type, 
                 simulator : Simulator,
                 # reward_fn : Callable,
                 render_mode=None, 
                 max_steps = 1000,
                 observation_space : spaces.Dict = spaces.Dict(),
                 action_space : spaces.Dict = spaces.Dict()): # empty string means just pure scenic???

        assert render_mode is None or render_mode in self.metadata["render_modes"]

        self.observation_space = observation_space
        self.action_space = action_space
        # self.reward_fn = reward_fn
        self.render_mode = render_mode
        self.max_steps = max_steps
        # self.simulator = simulator_type()
        self.simulator = simulator
        self.env = self.simulator.env # FIXME for one project only...a bit hacky should fix
        self.action_space = self.env.action_space # FIXME for one project only...a bit hacky should fix 
        self.observation_space = self.env.observation_space # FIXME for one project only...a bit hacky should fix
        self.scenario = scenario
        self.simulation_results = []

        self.feedback_result = None
        self.loop = None

    def _make_run_loop(self):
        scene, _ = self.scenario.generate(feedback=self.feedback_result)
        # steps_taken = 0
        while True:
            print("loop real restart")
            try:
                with self.simulator.simulateStepped(scene, maxSteps=self.max_steps) as simulation:
                    steps_taken = 0
                    print("Loop restart")
                    # this first block before the while loop is for the first reset call
                    done = lambda: not (simulation.result is None)
                    truncated = lambda: (steps_taken >= self.max_steps) # TODO handle cases where it is done right on maxsteps
                    print(f"done or truncated: {done() or truncated()}")
                    # FIXME, actually, on a second thought, this really should not be here, right?
                    # simulation.advance()
                    # steps_taken += 1
                    observation = simulation.get_obs()
                    info = simulation.get_info() 
                    print("first yielding")
                    actions = yield observation, info
                    print(f"actions received: {actions}")
                    simulation.actions = actions # TODO add action dict to simulation interfaces

                    while not done():
                        # Probably good that we advance first before any action is set.
                        # this is consistent with how reset works
                        simulation.advance()
                        steps_taken += 1
                        observation = simulation.get_obs()
                        info = simulation.get_info()
                        reward = simulation.get_reward()

                        # actions = yield observation, reward, done(), truncated(), info
                        if done():
                            # yield observation, reward, done(), truncated(), info
                            # actions = yield observation, reward, done(), truncated(), info
                            self.feedback_result = simulation.result
                            self.simulation_results.append(simulation.result)
                            simulation.destroy()
                            actions = yield observation, reward, done(), truncated(), info
                            break # a little unclean right here

                        actions = yield observation, reward, done(), truncated(), info
                        simulation.actions = actions # TODO add action dict to simulation interfaces
                        
            except ResetException:
                print("RESET RAISED")
                continue

    def reset(self, seed=None, options=None): # TODO will setting seed here conflict with VerifAI's setting of seed?
        # only setting enviornment seed, not torch seed?
        super().reset(seed=seed)
        if self.loop is None:
            self.loop = self._make_run_loop()
            observation, info = next(self.loop) # not doing self.scene.send(action) just yet
        else:
            print("looping")
            observation, info = self.loop.throw(ResetException())

        # try:
            # self.loop.close()
        # except:
            # self.loop = self._make_run_loop()
        # print("looping")
        # observation, info = next(self.loop) # not doing self.scene.send(action) just yet

        return observation, info
        
    def step(self, action):
        assert not (self.loop is None), "self.loop is None, have you called reset()?"

        observation, reward, terminated, truncated, info = self.loop.send(action)
        return observation, reward, terminated, truncated, info

    def render(self): # TODO figure out if this function has to be implemented here or if super() has default implementation
        """
        likely just going to be something like simulation.render() or something
        """
        # FIXME for one project only...also a bit hacky...
        self.env.render()

    def close(self):
        self.simulator.destroy()

