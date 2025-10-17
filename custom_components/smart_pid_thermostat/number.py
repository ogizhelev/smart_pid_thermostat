from homeassistant.components.number import NumberEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import *

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    async_add_entities([
        PIDNumber(hass, entry, CONF_TARGET, "Target Temperature", 5, 35, 0.1),
        PIDNumber(hass, entry, CONF_KP, "Kp", 0, 10, 0.01),
        PIDNumber(hass, entry, CONF_KI, "Ki", 0, 2, 0.001),
        PIDNumber(hass, entry, CONF_KD, "Kd", 0, 10, 0.01),
        PIDNumber(hass, entry, CONF_DEADBAND, "Deadband", 0, 2, 0.1),
    ], True)

class PIDNumber(NumberEntity):
    def __init__(self, hass, entry, key, label, min_v, max_v, step):
        self._hass = hass
        self._entry = entry
        self._key = key
        self._attr_name = f"{entry.title} {label}"
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_native_min_value = min_v
        self._attr_native_max_value = max_v
        self._attr_native_step = step
        self._attr_native_unit_of_measurement = "°C" if "temp" in key else None

    @property
    def value(self):
        cfg = {**DEFAULTS, **self._entry.data, **self._entry.options}
        return cfg[self._key]

    async def async_set_value(self, value: float):
        opts = {**self._entry.options}
        opts[self._key] = float(value)
        self._hass.config_entries.async_update_entry(self._entry, options=opts)
        self._hass.data[DOMAIN][self._entry.entry_id].update_config()

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(identifiers={(DOMAIN, self._entry.entry_id)}, name=self._entry.title, manufacturer="Smart PID")
