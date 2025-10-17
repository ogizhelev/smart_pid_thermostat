import logging
from datetime import timedelta, time as dtime

from homeassistant.core import HomeAssistant
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.helpers.event import async_track_time_interval, async_track_time_change

from .pid_controller import PIDController
from .autotune import RelayAutoTuner
from .const import *

_LOGGER = logging.getLogger(__name__)

class ControllerRuntime:
    """Holds the control loop state for a single config entry."""
    def __init__(self, hass: HomeAssistant, entry):
        self.hass = hass
        self.entry = entry
        self.cfg = {**DEFAULTS, **entry.data, **entry.options}
        # PID output interpreted as setpoint correction; clamp +/-5C per step
        self.pid = PIDController(self.cfg[CONF_KP], self.cfg[CONF_KI], self.cfg[CONF_KD], out_min=-5.0, out_max=5.0)
        self.enabled = True
        self.autotuner: RelayAutoTuner | None = None
        self._unsubs = []
        self._last_setpoint = self.cfg[CONF_TARGET]

    async def start(self):
        interval = timedelta(seconds=int(self.cfg[CONF_INTERVAL]))
        self._unsubs.append(async_track_time_interval(self.hass, self._loop, interval))

        if self.cfg.get(CONF_SETBACK_ENABLED, True):
            st = _parse_hms(self.cfg[CONF_SETBACK_TIME])
            rt = _parse_hms(self.cfg[CONF_RESTORE_TIME])
            self._unsubs.append(async_track_time_change(self.hass, self._on_setback, hour=st.hour, minute=st.minute, second=st.second))
            self._unsubs.append(async_track_time_change(self.hass, self._on_restore, hour=rt.hour, minute=rt.minute, second=rt.second))

    async def stop(self):
        for u in self._unsubs:
            u()
        self._unsubs.clear()

    def update_config(self):
        self.cfg = {**DEFAULTS, **self.entry.data, **self.entry.options}
        self.pid.kp = self.cfg[CONF_KP]
        self.pid.ki = self.cfg[CONF_KI]
        self.pid.kd = self.cfg[CONF_KD]

    async def _on_setback(self, now):
        await self._set_all_climates_temperature(self.cfg[CONF_SETBACK_TEMP])

    async def _on_restore(self, now):
        await self._set_all_climates_temperature(self.cfg[CONF_RESTORE_TEMP])
        fan = self.cfg.get(CONF_RESTORE_FAN)
        if fan:
            await self._set_all_climates_fan_mode(fan)

    async def _set_all_climates_temperature(self, temperature):
        climates = self.cfg[CONF_CLIMATES]
        await self.hass.services.async_call("climate", "set_temperature", {"entity_id": climates, "temperature": temperature}, blocking=False)

    async def _set_all_climates_fan_mode(self, fan):
        climates = self.cfg[CONF_CLIMATES]
        try:
            await self.hass.services.async_call("climate", "set_fan_mode", {"entity_id": climates, "fan_mode": fan}, blocking=False)
        except Exception as e:
            _LOGGER.debug("Fan mode set failed (maybe unsupported): %s", e)

    async def _loop(self, now):
        if not self.enabled:
            return

        sensor = self.hass.states.get(self.cfg[CONF_SENSOR])
        if not sensor or sensor.state in (STATE_UNAVAILABLE, "unknown", None):
            return
        try:
            ambient = float(sensor.state)
        except Exception:
            return

        target = float(self.cfg[CONF_TARGET])
        deadband = float(self.cfg[CONF_DEADBAND])

        if self.autotuner:
            commanded = self.autotuner.step(ambient, target)
            await self._set_all_climates_temperature(commanded)
            return

        error = target - ambient
        if abs(error) <= deadband:
            # hold; also reset integral to avoid drift
            self.pid.reset()
            return

        pid_output = self.pid.update(error)
        commanded = target + pid_output
        commanded = max(self.cfg[CONF_MIN_TEMP], min(self.cfg[CONF_MAX_TEMP], commanded))

        # Limit rate of change to avoid overshoot / thrash
        max_step = 0.5  # °C per loop
        prev = self._last_setpoint
        if commanded > prev + max_step:
            commanded = prev + max_step
        elif commanded < prev - max_step:
            commanded = prev - max_step
        self._last_setpoint = commanded

        await self._set_all_climates_temperature(commanded)

        _LOGGER.debug("[%s] ambient=%.2f target=%.2f error=%.2f out=%.2f set=%.2f",
                      self.cfg[CONF_NAME], ambient, target, error, pid_output, commanded)

    async def start_autotune(self):
        self.autotuner = RelayAutoTuner(amplitude=0.5)
        self.autotuner.start()

    async def stop_autotune(self):
        if not self.autotuner:
            return None
        res = self.autotuner.results()
        self.autotuner.stop()
        self.autotuner = None
        if res:
            new_opts = {**self.entry.options}
            new_opts[CONF_KP] = round(res["kp"], 4)
            new_opts[CONF_KI] = round(res["ki"], 4)
            new_opts[CONF_KD] = round(res["kd"], 4)
            self.hass.config_entries.async_update_entry(self.entry, options=new_opts)
        return res

def _parse_hms(hms: str):
    parts = [int(p) for p in hms.split(":")]
    while len(parts) < 3:
        parts.append(0)
    return dtime(parts[0], parts[1], parts[2])
