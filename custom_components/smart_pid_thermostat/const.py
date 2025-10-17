DOMAIN = "smart_pid_thermostat"

# Config entry keys
CONF_NAME = "name"
CONF_CLIMATES = "climates"
CONF_SENSOR = "sensor"
CONF_TARGET = "target_temperature"
CONF_KP = "kp"
CONF_KI = "ki"
CONF_KD = "kd"
CONF_MIN_TEMP = "min_temp"
CONF_MAX_TEMP = "max_temp"
CONF_INTERVAL = "update_interval"
CONF_DEADBAND = "deadband"
CONF_MODE = "mode"  # "auto", "heat", "cool"

# Night setback / restore
CONF_SETBACK_ENABLED = "setback_enabled"
CONF_SETBACK_TIME = "setback_time"        # "23:00:00"
CONF_SETBACK_TEMP = "setback_temp"        # 18
CONF_RESTORE_TIME = "restore_time"        # "06:30:00"
CONF_RESTORE_TEMP = "restore_temp"        # 23
CONF_RESTORE_FAN = "restore_fan"          # "auto", "low", "quiet"

DEFAULTS = {
    CONF_NAME: "Smart PID Controller",
    CONF_TARGET: 22.0,
    CONF_KP: 0.8,
    CONF_KI: 0.05,
    CONF_KD: 0.1,
    CONF_MIN_TEMP: 18.0,
    CONF_MAX_TEMP: 30.0,
    CONF_INTERVAL: 60,  # seconds
    CONF_DEADBAND: 0.3,
    CONF_MODE: "auto",
    CONF_SETBACK_ENABLED: True,
    CONF_SETBACK_TIME: "23:00:00",
    CONF_SETBACK_TEMP: 18.0,
    CONF_RESTORE_TIME: "06:30:00",
    CONF_RESTORE_TEMP: 23.0,
    CONF_RESTORE_FAN: "low",
}

# Platforms we expose (we'll provide number/switch/button/sensor for UI control)
PLATFORMS = ["number", "switch", "button", "sensor"]
