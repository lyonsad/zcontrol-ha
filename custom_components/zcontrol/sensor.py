"""Sensor platform for Z-Control integration."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import SIGNAL_STRENGTH_DECIBELS_MILLIWATT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import ZControlConfigEntry
from .const import DOMAIN
from .coordinator import ZControlCoordinator

_LOGGER = logging.getLogger(__name__)


SENSOR_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="wifi_signal",
        name="WiFi Signal",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        entity_registry_enabled_default=True,
    ),
    SensorEntityDescription(
        key="alarm_count",
        name="Alarm Count",
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=True,
    ),
    SensorEntityDescription(
        key="last_heartbeat",
        name="Last Heartbeat",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_registry_enabled_default=True,
    ),
    SensorEntityDescription(
        key="firmware",
        name="Firmware Version",
        entity_registry_enabled_default=False,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ZControlConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Z-Control sensors from a config entry."""
    coordinator = entry.runtime_data.coordinator

    entities: list[ZControlSensor] = []

    for device_id, device in coordinator.data.get("devices", {}).items():
        for description in SENSOR_DESCRIPTIONS:
            entities.append(
                ZControlSensor(
                    coordinator=coordinator,
                    device_id=device_id,
                    device=device,
                    description=description,
                )
            )

    async_add_entities(entities)


class ZControlSensor(CoordinatorEntity[ZControlCoordinator], SensorEntity):
    """Representation of a Z-Control sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ZControlCoordinator,
        device_id: str,
        device: dict[str, Any],
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._device_id = device_id
        self._attr_unique_id = f"{device_id}_{description.key}"

        # Device info for grouping entities
        device_name = device.get("deviceName")
        if not device_name:  # Handle empty string or None
            device_name = f"Z-Control {device_id}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=device_name,
            manufacturer="Zoeller",
            model=device.get("family", "Z-Control"),
            sw_version=device.get("firmwareVersion"),
            configuration_url="https://account.zcontrolcloud.com",
        )

    @property
    def _device_data(self) -> dict[str, Any] | None:
        """Get current device data from coordinator."""
        return self.coordinator.get_device(self._device_id)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return super().available and self._device_data is not None

    @property
    def native_value(self) -> Any:
        """Return the sensor value."""
        device = self._device_data
        if device is None:
            return None

        key = self.entity_description.key

        if key == "wifi_signal":
            # Get from deviceClass in first status entry
            status_list = device.get("deviceStatusList", [])
            if status_list:
                device_class = status_list[0].get("deviceClass", {})
                return device_class.get("rssiSignalStrength")
            return None

        if key == "alarm_count":
            return device.get("alarmCount", 0)

        if key == "last_heartbeat":
            # Parse the heartbeat timestamp
            heartbeat = device.get("lastHeartbeat")
            if heartbeat:
                # Try different formats
                for fmt in [
                    "%m-%d-%Y %I:%M:%S %p",  # "01-20-2026 6:20:41 PM"
                    "%Y-%m-%dT%H:%M:%S",      # ISO format
                    "%Y-%m-%dT%H:%M:%S.%f",   # ISO with microseconds
                ]:
                    try:
                        dt = datetime.strptime(heartbeat, fmt)
                        # API returns time in user's local timezone (from their account settings)
                        # Use HA's configured timezone
                        tz = ZoneInfo(self.coordinator.hass.config.time_zone)
                        return dt.replace(tzinfo=tz)
                    except ValueError:
                        continue
            return None

        if key == "firmware":
            return device.get("firmwareVersion")

        return None
