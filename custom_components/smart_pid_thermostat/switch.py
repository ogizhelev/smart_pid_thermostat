from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    async_add_entities([SmartPIDEnableSwitch(hass, entry)], True)

class SmartPIDEnableSwitch(SwitchEntity):
    def __init__(self, hass, entry):
        self._hass = hass
        self._entry = entry
        self._is_on = True
        self._attr_name = f"{entry.title} Enabled"
        self._attr_unique_id = f"{entry.entry_id}_enabled"

    @property
    def is_on(self):
        return self._is_on

    async def async_turn_on(self, **kwargs):
        self._is_on = True
        self._hass.data[DOMAIN][self._entry.entry_id].enabled = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        self._is_on = False
        self._hass.data[DOMAIN][self._entry.entry_id].enabled = False
        self.async_write_ha_state()

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(identifiers={(DOMAIN, self._entry.entry_id)}, name=self._entry.title, manufacturer="Smart PID")
