from __future__ import annotations
import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform

from .const import DOMAIN, PLATFORMS
from .coordinator import ControllerRuntime

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    runtime = ControllerRuntime(hass, entry)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = runtime
    await runtime.start()

    await hass.config_entries.async_forward_entry_setups(entry, [Platform.SENSOR, Platform.SWITCH, Platform.NUMBER, Platform.BUTTON])

    async def handle_start_autotune(call):
        await runtime.start_autotune()

    async def handle_stop_autotune(call):
        res = await runtime.stop_autotune()
        _LOGGER.info("Auto-tune result: %s", res)

    hass.services.async_register(DOMAIN, "start_autotune", handle_start_autotune)
    hass.services.async_register(DOMAIN, "stop_autotune", handle_stop_autotune)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    runtime: ControllerRuntime = hass.data[DOMAIN].pop(entry.entry_id, None)
    if runtime:
        await runtime.stop()
    unload_ok = await hass.config_entries.async_unload_platforms(entry, [Platform.SENSOR, Platform.SWITCH, Platform.NUMBER, Platform.BUTTON])
    return unload_ok
