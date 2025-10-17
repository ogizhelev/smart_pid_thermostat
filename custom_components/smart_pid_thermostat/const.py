DOMAIN = "smart_pid_thermostat"

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
CONF_MODE = "mode"  # informational only

CONF_SETBACK_ENABLED = "setback_enabled"
CONF_SETBACK_TIME = "setback_time"
CONF_SETBACK_TEMP = "setback_temp"
CONF_RESTORE_TIME = "restore_time"
CONF_RESTORE_TEMP = "restore_temp"
CONF_RESTORE_FAN = "restore_fan"

DEFAULTS = {
    CONF_NAME: "Smart PID Controller",
    CONF_TARGET: 22.0,
    CONF_KP: 0.8,
    CONF_KI: 0.05,
    CONF_KD: 0.1,
    CONF_MIN_TEMP: 18.0,
    CONF_MAX_TEMP: 30.0,
    CONF_INTERVAL: 60,
    CONF_DEADBAND: 0.2,
    CONF_MODE: "auto",
    CONF_SETBACK_ENABLED: True,
    CONF_SETBACK_TIME: "23:00:00",
    CONF_SETBACK_TEMP: 18.0,
    CONF_RESTORE_TIME: "06:30:00",
    CONF_RESTORE_TEMP: 23.0,
    CONF_RESTORE_FAN: "low",
}

PLATFORMS = ["number", "switch", "button", "sensor"]
