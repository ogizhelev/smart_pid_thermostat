from __future__ import annotations
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    EntitySelector, EntitySelectorConfig,
    NumberSelector, NumberSelectorConfig,
    SelectSelector, SelectSelectorConfig, SelectOptionDict,
    DurationSelector, DurationSelectorConfig,
    TextSelector, TextSelectorConfig,
)

from .const import *

class SmartPIDConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title=user_input.get(CONF_NAME, "Smart PID Controller"), data=user_input)

        schema = vol.Schema({
            vol.Required(CONF_NAME, default=DEFAULTS[CONF_NAME]): TextSelector(TextSelectorConfig()),
            vol.Required(CONF_CLIMATES): EntitySelector(EntitySelectorConfig(domain=['climate'], multiple=True)),
            vol.Required(CONF_SENSOR): EntitySelector(EntitySelectorConfig(domain=['sensor'], multiple=False)),
            vol.Required(CONF_TARGET, default=DEFAULTS[CONF_TARGET]): NumberSelector(NumberSelectorConfig(min=5, max=35, step=0.1, mode='box')),
            vol.Required(CONF_MIN_TEMP, default=DEFAULTS[CONF_MIN_TEMP]): NumberSelector(NumberSelectorConfig(min=5, max=35, step=0.5, mode='box')),
            vol.Required(CONF_MAX_TEMP, default=DEFAULTS[CONF_MAX_TEMP]): NumberSelector(NumberSelectorConfig(min=5, max=35, step=0.5, mode='box')),
            vol.Required(CONF_DEADBAND, default=DEFAULTS[CONF_DEADBAND]): NumberSelector(NumberSelectorConfig(min=0, max=2, step=0.1, mode='box')),
            vol.Required(CONF_MODE, default=DEFAULTS[CONF_MODE]): SelectSelector(SelectSelectorConfig(options=[
                SelectOptionDict(value='auto', label='Auto'),
                SelectOptionDict(value='heat', label='Heat'),
                SelectOptionDict(value='cool', label='Cool'),
            ])),
            vol.Required(CONF_KP, default=DEFAULTS[CONF_KP]): NumberSelector(NumberSelectorConfig(min=0, max=10, step=0.01, mode='box')),
            vol.Required(CONF_KI, default=DEFAULTS[CONF_KI]): NumberSelector(NumberSelectorConfig(min=0, max=2, step=0.001, mode='box')),
            vol.Required(CONF_KD, default=DEFAULTS[CONF_KD]): NumberSelector(NumberSelectorConfig(min=0, max=10, step=0.01, mode='box')),
            vol.Required(CONF_INTERVAL, default=DEFAULTS[CONF_INTERVAL]): NumberSelector(NumberSelectorConfig(min=15, max=900, step=5, mode='slider')),
            vol.Required(CONF_SETBACK_ENABLED, default=DEFAULTS[CONF_SETBACK_ENABLED]): SelectSelector(SelectSelectorConfig(options=[
                SelectOptionDict(value=True, label='Enabled'),
                SelectOptionDict(value=False, label='Disabled'),
            ])),
            vol.Required(CONF_SETBACK_TIME, default=DEFAULTS[CONF_SETBACK_TIME]): TextSelector(TextSelectorConfig(type='text')),
            vol.Required(CONF_SETBACK_TEMP, default=DEFAULTS[CONF_SETBACK_TEMP]): NumberSelector(NumberSelectorConfig(min=5, max=30, step=0.5, mode='box')),
            vol.Required(CONF_RESTORE_TIME, default=DEFAULTS[CONF_RESTORE_TIME]): TextSelector(TextSelectorConfig(type='text')),
            vol.Required(CONF_RESTORE_TEMP, default=DEFAULTS[CONF_RESTORE_TEMP]): NumberSelector(NumberSelectorConfig(min=10, max=35, step=0.5, mode='box')),
            vol.Required(CONF_RESTORE_FAN, default=DEFAULTS[CONF_RESTORE_FAN]): SelectSelector(SelectSelectorConfig(options=[
                SelectOptionDict(value='auto', label='Auto'),
                SelectOptionDict(value='low', label='Low'),
                SelectOptionDict(value='quiet', label='Quiet'),
            ])),
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        cfg = {**DEFAULTS, **self.config_entry.data, **self.config_entry.options}
        schema = vol.Schema({
            vol.Required(CONF_TARGET, default=cfg[CONF_TARGET]): NumberSelector(NumberSelectorConfig(min=5, max=35, step=0.1, mode='box')),
            vol.Required(CONF_KP, default=cfg[CONF_KP]): NumberSelector(NumberSelectorConfig(min=0, max=10, step=0.01, mode='box')),
            vol.Required(CONF_KI, default=cfg[CONF_KI]): NumberSelector(NumberSelectorConfig(min=0, max=2, step=0.001, mode='box')),
            vol.Required(CONF_KD, default=cfg[CONF_KD]): NumberSelector(NumberSelectorConfig(min=0, max=10, step=0.01, mode='box')),
            vol.Required(CONF_MIN_TEMP, default=cfg[CONF_MIN_TEMP]): NumberSelector(NumberSelectorConfig(min=5, max=35, step=0.5, mode='box')),
            vol.Required(CONF_MAX_TEMP, default=cfg[CONF_MAX_TEMP]): NumberSelector(NumberSelectorConfig(min=5, max=35, step=0.5, mode='box')),
            vol.Required(CONF_DEADBAND, default=cfg[CONF_DEADBAND]): NumberSelector(NumberSelectorConfig(min=0, max=2, step=0.1, mode='box')),
            vol.Required(CONF_INTERVAL, default=cfg[CONF_INTERVAL]): NumberSelector(NumberSelectorConfig(min=15, max=900, step=5, mode='slider')),
            vol.Required(CONF_SETBACK_ENABLED, default=cfg[CONF_SETBACK_ENABLED]): SelectSelector(SelectSelectorConfig(options=[
                SelectOptionDict(value=True, label='Enabled'),
                SelectOptionDict(value=False, label='Disabled'),
            ])),
            vol.Required(CONF_SETBACK_TIME, default=cfg[CONF_SETBACK_TIME]): TextSelector(TextSelectorConfig(type='text')),
            vol.Required(CONF_SETBACK_TEMP, default=cfg[CONF_SETBACK_TEMP]): NumberSelector(NumberSelectorConfig(min=5, max=30, step=0.5, mode='box')),
            vol.Required(CONF_RESTORE_TIME, default=cfg[CONF_RESTORE_TIME]): TextSelector(TextSelectorConfig(type='text')),
            vol.Required(CONF_RESTORE_TEMP, default=cfg[CONF_RESTORE_TEMP]): NumberSelector(NumberSelectorConfig(min=10, max=35, step=0.5, mode='box')),
            vol.Required(CONF_RESTORE_FAN, default=cfg[CONF_RESTORE_FAN]): SelectSelector(SelectSelectorConfig(options=[
                SelectOptionDict(value='auto', label='Auto'),
                SelectOptionDict(value='low', label='Low'),
                SelectOptionDict(value='quiet', label='Quiet'),
            ])),
        })
        return self.async_show_form(step_id="init", data_schema=schema)
