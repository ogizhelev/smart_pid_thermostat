from __future__ import annotations
import time

class RelayAutoTuner:
    """Simple relay auto-tuner to estimate Ku/Tu for PID.
    This toggles an offset around target and measures oscillation period & amplitude.
    It's a lightweight approach suitable for HVAC with slow dynamics.
    """
    def __init__(self, amplitude=0.5, settle_cycles=1, measure_cycles=3):
        self.amp = amplitude
        self.settle_cycles = settle_cycles
        self.measure_cycles = measure_cycles
        self.reset()

    def reset(self):
        self.peaks = []
        self.last_value = None
        self.state = 1  # 1 or -1
        self.last_switch_t = None
        self.cycle_count = 0
        self.running = False

    def start(self):
        self.reset()
        self.running = True

    def stop(self):
        self.running = False

    def step(self, ambient_value: float, target: float, now: float | None = None):
        """Returns commanded target (target +/- amp) while running.
        This function should be called periodically with latest ambient_value.
        """
        t = now or time.monotonic()
        if not self.running:
            return target

        # Simple relay: if ambient above (target), drive target lower, else higher
        if ambient_value > target:
            self.state = -1
        else:
            self.state = 1

        commanded = target + (self.state * self.amp)

        # Detect peaks (zero-crossings derivative change). For simplicity we track sign changes
        # of (ambient - target).
        sign = 1 if (ambient_value - target) >= 0 else -1
        if self.last_value is not None:
            last_sign = 1 if (self.last_value - target) >= 0 else -1
            if sign != last_sign:
                self.cycle_count += 0.5  # half cycle
                self.peaks.append((t, ambient_value))
        self.last_value = ambient_value

        return commanded

    def results(self):
        """Estimate Ku and Tu from peak timings; then suggest PID via Ziegler–Nichols.
        Returns dict or None if insufficient data.
        """
        if len(self.peaks) < 4:
            return None
        # Estimate period Tu from time between every two peaks of same sign (~2 indices apart)
        ts = [p[0] for p in self.peaks]
        if len(ts) < 4:
            return None
        periods = []
        for i in range(0, len(ts) - 2):
            dt = ts[i+2] - ts[i]
            if dt > 0:
                periods.append(dt)
        if not periods:
            return None
        Tu = sum(periods) / len(periods)

        # Ultimate gain Ku approximated via describing function of relay ~ (4 * amplitude)/(pi * A)
        # Here A ~ average peak amplitude over target
        amps = [abs(p[1]) for p in self.peaks]
        if not amps:
            return None
        A = max(1e-6, (sum(amps) / len(amps)))
        Ku = (4 * self.amp) / (3.14159 * A)

        # ZN classic rules:
        Kp = 0.6 * Ku
        Ki = 2 * Kp / Tu
        Kd = Kp * Tu / 8

        return {"Ku": Ku, "Tu": Tu, "kp": Kp, "ki": Ki, "kd": Kd}
