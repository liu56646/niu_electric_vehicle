"""
Constants for Niu Electric Vehicle integration.
"""
from homeassistant.const import Platform

DOMAIN = "niu_electric_vehicle"
PLATFORMS = [Platform.SENSOR]

# Configuration
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_VEHICLE_ID = "vehicle_id"

# Data
DATA_COORDINATOR = "coordinator"

# Defaults
DEFAULT_SCAN_INTERVAL = 300  # 5 minutes

# Vehicle data keys
VEHICLE_STATUS = "vehicle_status"
VEHICLE_BATTERY = "battery_level"
VEHICLE_RANGE = "range"
VEHICLE_SPEED = "speed"
VEHICLE_MILEAGE = "mileage"
VEHICLE_POSITION = "position"
VEHICLE_TEMP = "temperature"
VEHICLE_LIGHT = "light_status"
VEHICLE_LOCK = "lock_status"