import time

class RelayAutoTuner:
    """Simple relay autotuner for Ku/Tu -> Ziegler–Nichols gains."""
    def __init__(self, amplitude=0.5):
        self.amp = amplitude
        self.reset()

    def reset(self):
        self.peaks = []
        self.last_value = None
        self.state = 1
        self.running = False

    def start(self):
        self.reset()
        self.running = True

    def stop(self):
        self.running = False

    def step(self, ambient_value, target, now=None):
        t = now or time.monotonic()
        if not self.running:
            return target

        self.state = -1 if ambient_value > target else 1
        commanded = target + (self.state * self.amp)

        sign = 1 if (ambient_value - target) >= 0 else -1
        if self.last_value is not None:
            last_sign = 1 if (self.last_value - target) >= 0 else -1
            if sign != last_sign:
                self.peaks.append((t, ambient_value))
        self.last_value = ambient_value
        return commanded

    def results(self):
        if len(self.peaks) < 4:
            return None
        ts = [p[0] for p in self.peaks]
        periods = []
        for i in range(0, len(ts) - 2):
            dt = ts[i+2] - ts[i]
            if dt > 0:
                periods.append(dt)
        if not periods:
            return None
        Tu = sum(periods) / len(periods)
        amps = [abs(p[1]) for p in self.peaks]
        if not amps:
            return None
        A = max(1e-6, (sum(amps) / len(amps)))
        Ku = (4 * self.amp) / (3.14159 * A)
        Kp = 0.6 * Ku
        Ki = 2 * Kp / Tu
        Kd = Kp * Tu / 8
        return {"Ku": Ku, "Tu": Tu, "kp": Kp, "ki": Ki, "kd": Kd}
