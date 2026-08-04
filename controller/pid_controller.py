import numpy as np
from cloudpendulumclient.benchmark.controller import ControllerBase, MotorState

class PointPIDController(ControllerBase):
    def __init__(self):
        self.torque_limit = [0.12, 0.12]
        self.dt = 0.002

        # default weights
        self.Kp = 0.2
        self.Ki = 0.00
        self.Kd = 0.01
        self.goal = np.array([np.pi, 0.0])

        # init pars
        self.errors1 = []
        self.errors2 = []
        self.errorsum1 = 0.0
        self.errorsum2 = 0.0

    def get_control_output(
        self,
        state: list[MotorState],
    ) -> list[float]:
        assert len(state) == 2

        e1 = self.goal[0] - state[0].position
        e2 = self.goal[1] - state[1].position
        # e1 = (e1 + np.pi) % (2*np.pi) - np.pi
        # e2 = (e2 + np.pi) % (2*np.pi) - np.pi
        self.errors1.append(e1)
        self.errors2.append(e2)
        self.errorsum1 += e1
        self.errorsum2 += e2

        P1 = self.Kp * e1
        P2 = self.Kp * e2

        # I1 = self.Ki * np.sum(np.asarray(self.errors1)) * self.dt
        # I2 = self.Ki * np.sum(np.asarray(self.errors2)) * self.dt
        I1 = self.Ki * self.errorsum1 * self.dt
        I2 = self.Ki * self.errorsum2 * self.dt
        if len(self.errors1) > 2:
            D1 = self.Kd * (self.errors1[-1] - self.errors1[-2]) / self.dt
            D2 = self.Kd * (self.errors2[-1] - self.errors2[-2]) / self.dt
        else:
            D1 = 0.0
            D2 = 0.0

        D1 = np.clip(D1, min(-P1, 0.0), max(-P1, 0.0))
        D2 = np.clip(D2, min(-P1, 0.0), max(-P1, 0.0))

        u1 = P1 + I1 + D1
        u2 = P2 + I2 + D2

        u1 = np.clip(u1, -self.torque_limit[0], self.torque_limit[0])
        u2 = np.clip(u2, -self.torque_limit[1], self.torque_limit[1])
        return [u1, u2]
