from go1_gym_deploy.utils.deployment_runner import DeploymentRunner

from MPC_Controller.robot_runner.RobotRunnerFSM import RobotRunnerFSM
from MPC_Controller.common.Quadruped import RobotType

class MPCDeploymentRunner(DeploymentRunner):
    def __init__(self, experiment_name="unnamed", se=None, log_root="."):
        super().__init__(experiment_name, se, log_root)
        self.robot_runner = RobotRunnerFSM()
        self.robot_runner.init(RobotType["GO1"])

    def add_open_loop_agent(self, agent, name):
        raise NotImplementedError()

    def add_control_agent(self, agent, name):
        return super().add_control_agent(agent, name)

    def add_vision_server(self, vision_server):
        raise NotImplementedError()

    def set_command_agents(self, name):
        raise NotImplementedError()

    def add_policy(self, policy):
        raise NotImplementedError()

    def add_command_profile(self, command_profile):
        return super().add_command_profile(command_profile)


    def run(self, num_log_steps=1000000000, max_steps=100000000, logging=True):
        assert self.control_agent_name is not None, "cannot deploy, runner has no control agent!"
        assert self.command_profile is not None, "cannot deploy, runner has no command profile!"

        # TODO: add basic test for comms

        for agent_name in self.agents.keys():
            obs = self.agents[agent_name].reset()
            if agent_name == self.control_agent_name:
                control_obs = obs

        control_obs = self.calibrate(wait=True)

        # now, run control loop

        try:
            for i in range(max_steps):
                
                vel_command = control_obs['obs'][0, 3:6]
                print(vel_command)
                dof_pos = self.state_estimator.get_dof_pos()
                dof_vel = self.state_estimator.get_dof_vel()
                dof_states = {
                    'pos': dof_pos,
                    'vel': dof_vel
                }

                body_quat = self.state_estimator.get_body_quat()
                # NOTE: NOT IMPLEMENTED!
                body_loc = self.state_estimator.get_body_loc()

                body_w = self.state_estimator.get_body_angular_vel()
                # NOTE: NOT IMPLEMENTED!
                body_v = self.state_estimator.get_body_linear_vel()

                body_state = {
                    'pose': {
                        'p': body_loc,
                        'r': body_quat
                    },
                    'vel': {
                        'linear': body_v,
                        'angular': body_w
                    }
                }

                torque_target = self.robot_runner.run(dof_states, body_state, vel_command)
                print(torque_target)
                input()
                #action = self.policy(control_obs, policy_info)

                for agent_name in self.agents.keys():
                    obs, ret, done, info = self.agents[agent_name].step(torque_target, direct_torque=True)

                    info.update(policy_info)
                    info.update({"observation": obs, "reward": ret, "done": done, "timestep": i,
                                 "time": i * self.agents[self.control_agent_name].dt, "action": None, "rpy": self.agents[self.control_agent_name].se.get_rpy(), "torques": self.agents[self.control_agent_name].torques})

                    if logging: self.logger.log(agent_name, info)

                    if agent_name == self.control_agent_name:
                        control_obs, control_ret, control_done, control_info = obs, ret, done, info

                # bad orientation emergency stop
                rpy = self.agents[self.control_agent_name].se.get_rpy()
                if abs(rpy[0]) > 1.6 or abs(rpy[1]) > 1.6:
                    self.calibrate(wait=False, low=True)

                # check for logging command
                prev_button_states = self.button_states[:]
                self.button_states = self.command_profile.get_buttons()

                if self.state_estimator.left_lower_left_switch_pressed:
                    if not self.is_currently_probing:
                        print("START LOGGING")
                        self.is_currently_probing = True
                        self.agents[self.control_agent_name].set_probing(True)
                        self.init_log_filename()
                        self.logger.reset()
                    else:
                        print("SAVE LOG")
                        self.is_currently_probing = False
                        self.agents[self.control_agent_name].set_probing(False)
                        # calibrate, log, and then resume control
                        control_obs = self.calibrate(wait=False)
                        self.logger.save(self.log_filename)
                        self.init_log_filename()
                        self.logger.reset()
                        time.sleep(1)
                        control_obs = self.agents[self.control_agent_name].reset()
                    self.state_estimator.left_lower_left_switch_pressed = False

                for button in range(4):
                    if self.command_profile.currently_triggered[button]:
                        if not self.is_currently_logging[button]:
                            print("START LOGGING")
                            self.is_currently_logging[button] = True
                            self.init_log_filename()
                            self.logger.reset()
                    else:
                        if self.is_currently_logging[button]:
                            print("SAVE LOG")
                            self.is_currently_logging[button] = False
                            # calibrate, log, and then resume control
                            control_obs = self.calibrate(wait=False)
                            self.logger.save(self.log_filename)
                            self.init_log_filename()
                            self.logger.reset()
                            time.sleep(1)
                            control_obs = self.agents[self.control_agent_name].reset()

                if self.state_estimator.right_lower_right_switch_pressed:
                    control_obs = self.calibrate(wait=False)
                    time.sleep(1)
                    self.state_estimator.right_lower_right_switch_pressed = False
                    # self.button_states = self.command_profile.get_buttons()
                    while not self.state_estimator.right_lower_right_switch_pressed:
                        time.sleep(0.01)
                        # self.button_states = self.command_profile.get_buttons()
                    self.state_estimator.right_lower_right_switch_pressed = False

            # finally, return to the nominal pose
            control_obs = self.calibrate(wait=False)
            self.logger.save(self.log_filename)

        except KeyboardInterrupt:
            self.logger.save(self.log_filename)
