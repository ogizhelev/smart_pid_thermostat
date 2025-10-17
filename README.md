# Smart PID Thermostat
#
PID-based controller for Home Assistant that **adjusts temperature and fan only** (never changes HVAC mode).  
Keeps your rooms close to target temp; great with inverter A/C and fan coils.

## Install via HACS

1. Add repository to HACS:  
   [![Add in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=ogizhelev&repository=smart_pid_thermostat&category=integration)

2. Install **Smart PID Thermostat** from HACS → Integrations.

3. Add the integration (Config Flow):  
   [![Add Integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=smart_pid_thermostat)

## What it does
- PID loop targets ambient temperature using your sensor
- Sends `climate.set_temperature` and `climate.set_fan_mode` (low/quiet/auto)
- Night setback & morning restore
- Autotune button to estimate PID gains

## What it doesn't do
- No `hvac_mode` changes (heat/cool/off)
- No power toggling

## Multiple instances
Create as many controllers as you need (e.g., per room/zone). Each instance can control one or **many climates**.

MIT © ogizhelev
