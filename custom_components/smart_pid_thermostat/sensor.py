from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    async_add_entities([SmartPIDStatusSensor(hass, entry)], True)

class SmartPIDStatusSensor(SensorEntity):
    def __init__(self, hass, entry):
        self._hass = hass
        self._entry = entry
        self._attr_name = f"{entry.title} Status"
        self._attr_unique_id = f"{entry.entry_id}_status"
        self._attr_native_value = "idle"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(identifiers={(DOMAIN, self._entry.entry_id)}, name=self._entry.title, manufacturer="Smart PID")

    async def async_update(self):
        runtime = self._hass.data[DOMAIN][self._entry.entry_id]
        if getattr(runtime, "autotuner", None):
            self._attr_native_value = "autotuning"
        else:
            self._attr_native_value = "running"
