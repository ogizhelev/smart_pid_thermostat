from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    async_add_entities([AutotuneStartButton(hass, entry), AutotuneStopButton(hass, entry)], True)

class AutotuneStartButton(ButtonEntity):
    def __init__(self, hass, entry):
        self._hass = hass
        self._entry = entry
        self._attr_name = f"{entry.title} Start Autotune"
        self._attr_unique_id = f"{entry.entry_id}_autotune_start"

    async def async_press(self, **kwargs):
        await self._hass.data[DOMAIN][self._entry.entry_id].start_autotune()

    @property
    def device_info(self):
        return DeviceInfo(identifiers={(DOMAIN, self._entry.entry_id)}, name=self._entry.title, manufacturer="Smart PID")

class AutotuneStopButton(ButtonEntity):
    def __init__(self, hass, entry):
        self._hass = hass
        self._entry = entry
        self._attr_name = f"{entry.title} Stop Autotune & Apply"
        self._attr_unique_id = f"{entry.entry_id}_autotune_stop"

    async def async_press(self, **kwargs):
        await self._hass.data[DOMAIN][self._entry.entry_id].stop_autotune()

    @property
    def device_info(self):
        return DeviceInfo(identifiers={(DOMAIN, self._entry.entry_id)}, name=self._entry.title, manufacturer="Smart PID")
