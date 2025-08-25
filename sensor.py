"""
Sensor platform for Niu Electric Vehicle integration.
"""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    LENGTH_KILOMETERS,
    SPEED_KILOMETERS_PER_HOUR,
    TEMP_CELSIUS,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import (
    DATA_COORDINATOR,
    DOMAIN,
    VEHICLE_BATTERY,
    VEHICLE_LIGHT,
    VEHICLE_LOCK,
    VEHICLE_MILEAGE,
    VEHICLE_POSITION,
    VEHICLE_RANGE,
    VEHICLE_SPEED,
    VEHICLE_STATUS,
    VEHICLE_TEMP,
)
from .coordinator import NiuDataCoordinator

_LOGGER = logging.getLogger(__name__)

SENSOR_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key=VEHICLE_BATTERY,
        name="Battery Level",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key=VEHICLE_RANGE,
        name="Range",
        native_unit_of_measurement=LENGTH_KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key=VEHICLE_SPEED,
        name="Current Speed",
        native_unit_of_measurement=SPEED_KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key=VEHICLE_MILEAGE,
        name="Total Mileage",
        native_unit_of_measurement=LENGTH_KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key=VEHICLE_TEMP,
        name="Temperature",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Niu Electric Vehicle sensors from a config entry."""
    coordinator: NiuDataCoordinator = hass.data[DOMAIN][DATA_COORDINATOR][entry.entry_id]

    entities: list[NiuSensor] = []
    for description in SENSOR_DESCRIPTIONS:
        entities.append(NiuSensor(coordinator, description))

    async_add_entities(entities)

class NiuSensor(SensorEntity):
    """Representation of a Niu Electric Vehicle sensor."""

    def __init__(
        self, coordinator: NiuDataCoordinator, description: SensorEntityDescription
    ) -> None:
        """Initialize the sensor."""
        self.entity_description = description
        self.coordinator = coordinator
        self._attr_unique_id = f"{coordinator.vehicle_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.vehicle_id)},
            "name": f"Niu Vehicle {coordinator.vehicle_id}",
            "manufacturer": "Niu Technologies",
        }

    @property
    def native_value(self) -> StateType:
        """Return the value reported by the sensor."""
        data = self.coordinator.data

        if self.entity_description.key == VEHICLE_BATTERY:
            return data.get("battery", {}).get("level")
        if self.entity_description.key == VEHICLE_RANGE:
            return data.get("range")
        if self.entity_description.key == VEHICLE_SPEED:
            return data.get("speed")
        if self.entity_description.key == VEHICLE_MILEAGE:
            return data.get("mileage")
        if self.entity_description.key == VEHICLE_TEMP:
            return data.get("temperature")

        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.last_update_success

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_update(self) -> None:
        """Update the entity."""
        await self.coordinator.async_request_refresh()