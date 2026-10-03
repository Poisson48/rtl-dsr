"""Binary sensor platform for the RTL-SDR integration."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import RtlDsrCoordinator
from .entity import RtlDsrEntity

BINARY_SENSORS: tuple[BinarySensorEntityDescription, ...] = (
    BinarySensorEntityDescription(
        key="connected",
        translation_key="connected",
        name="Connected",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
    BinarySensorEntityDescription(
        key="signal_detected",
        translation_key="signal_detected",
        name="Signal detected",
        device_class=BinarySensorDeviceClass.SOUND,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: RtlDsrCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([RtlDsrBinarySensor(coordinator, d) for d in BINARY_SENSORS])


class RtlDsrBinarySensor(RtlDsrEntity, BinarySensorEntity):
    """Binary sensor exposing dongle state."""

    entity_description: BinarySensorEntityDescription

    def __init__(
        self,
        coordinator: RtlDsrCoordinator,
        description: BinarySensorEntityDescription,
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        data = self.coordinator.data
        if data is None:
            return None
        key = self.entity_description.key
        if key == "connected":
            return data.connected
        if key == "signal_detected":
            if data.peak_power is None or self.coordinator.squelch is None:
                return False
            return data.peak_power > self.coordinator.squelch
        return None
