from __future__ import annotations
import time

class PIDController:
    def __init__(self, kp: float, ki: float, kd: float, out_min=None, out_max=None):
        self.kp = float(kp)
        self.ki = float(ki)
        self.kd = float(kd)
        self.out_min = out_min
        self.out_max = out_max
        self.reset()

    def reset(self):
        self._i = 0.0
        self._last_error = None
        self._last_t = None

    def update(self, error: float, now: float | None = None) -> float:
        t = now if now is not None else time.monotonic()
        if self._last_t is None:
            dt = 1.0
        else:
            dt = max(1e-3, t - self._last_t)
        self._last_t = t

        # P
        p = self.kp * error

        # I with simple anti-windup clamp via output clamp later
        self._i += self.ki * error * dt

        # D
        d = 0.0
        if self._last_error is not None:
            d = self.kd * (error - self._last_error) / dt
        self._last_error = error

        out = p + self._i + d
        # clamp output and reflect on integral if clamped
        if self.out_min is not None and out < self.out_min:
            out = self.out_min
        if self.out_max is not None and out > self.out_max:
            out = self.out_max
        return out
