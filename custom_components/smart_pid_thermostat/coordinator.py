from __future__ import annotations
import logging
from datetime import timedelta, datetime, time as dtime

from homeassistant.core import HomeAssistant, callback
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.helpers.event import async_track_time_interval, async_track_time_change

from .pid_controller import PIDController
from .autotune import RelayAutoTuner
from .const import *

_LOGGER = logging.getLogger(__name__)

class ControllerRuntime:
    def __init__(self, hass: HomeAssistant, entry):
        self.hass = hass
        self.entry = entry
        self.cfg = {**DEFAULTS, **entry.data, **entry.options}
        self.pid = PIDController(
            self.cfg[CONF_KP],
            self.cfg[CONF_KI],
            self.cfg[CONF_KD],
            out_min=self.cfg[CONF_MIN_TEMP],
            out_max=self.cfg[CONF_MAX_TEMP],
        )
        self.enabled = True
        self.autotuner: RelayAutoTuner | None = None
        self._unsubs = []

    async def start(self):
        # periodic control loop
        interval = timedelta(seconds=int(self.cfg[CONF_INTERVAL]))
        self._unsubs.append(async_track_time_interval(self.hass, self._loop, interval))

        # night setback and restore
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
        temp = float(self.cfg[CONF_SETBACK_TEMP])
        await self._set_all_climates_temperature(temp)

    async def _on_restore(self, now):
        temp = float(self.cfg[CONF_RESTORE_TEMP])
        await self._set_all_climates_temperature(temp)
        fan = self.cfg.get(CONF_RESTORE_FAN)
        if fan:
            await self._set_all_climates_fan_mode(fan)

    async def _set_all_climates_temperature(self, temperature: float):
        climates = self.cfg[CONF_CLIMATES]
        await self.hass.services.async_call("climate", "set_temperature", {
            "entity_id": climates,
            "temperature": temperature
        }, blocking=False)

    async def _set_all_climates_fan_mode(self, fan: str):
        climates = self.cfg[CONF_CLIMATES]
        try:
            await self.hass.services.async_call("climate", "set_fan_mode", {
                "entity_id": climates,
                "fan_mode": fan
            }, blocking=False)
        except Exception as e:
            _LOGGER.debug("Fan mode set failed (maybe unsupported): %s", e)

    async def _loop(self, now):
        if not self.enabled:
            return

        sensor = self.hass.states.get(self.cfg[CONF_SENSOR])
        if not sensor or sensor.state in (STATE_UNAVAILABLE, "unknown", None):
            _LOGGER.debug("Sensor %s unavailable", self.cfg[CONF_SENSOR])
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
            return

        out = self.pid.update(error)
        # Interpret PID output as absolute setpoint around target
        commanded = max(self.cfg[CONF_MIN_TEMP], min(self.cfg[CONF_MAX_TEMP], target + out))
        await self._set_all_climates_temperature(commanded)

    # Service hooks
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
            # Apply suggested gains to options
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
