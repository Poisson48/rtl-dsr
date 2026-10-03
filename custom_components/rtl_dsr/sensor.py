"""Sensor platform for the RTL-SDR integration."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfFrequency
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    ATTR_SPECTRUM_NOISE_FLOOR,
    ATTR_SPECTRUM_PEAK,
    ATTR_SPECTRUM_PEAK_FREQ,
    DOMAIN,
)
from .coordinator import RtlDsrCoordinator
from .entity import RtlDsrEntity

SENSORS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="rssi",
        translation_key="rssi",
        name="Signal (RSSI)",
        native_unit_of_measurement="dB",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="noise_floor",
        translation_key="noise_floor",
        name="Noise floor",
        native_unit_of_measurement="dB",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="peak_freq",
        translation_key="peak_freq",
        name="Peak frequency",
        native_unit_of_measurement=UnitOfFrequency.MEGAHERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=3,
    ),
    SensorEntityDescription(
        key="peak_power",
        translation_key="peak_power",
        name="Peak power",
        native_unit_of_measurement="dB",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="tuner_type",
        translation_key="tuner_type",
        name="Tuner",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="serial",
        translation_key="serial",
        name="Serial",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from a config entry."""
    coordinator: RtlDsrCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([RtlDsrSensor(coordinator, d) for d in SENSORS])


class RtlDsrSensor(RtlDsrEntity, SensorEntity):
    """A single RTL-SDR measurement."""

    entity_description: SensorEntityDescription

    def __init__(
        self, coordinator: RtlDsrCoordinator, description: SensorEntityDescription
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self):
        data = self.coordinator.data
        if data is None:
            return None
        key = self.entity_description.key
        if key == "rssi":
            return data.rssi
        if key == "noise_floor":
            return data.noise_floor
        if key == "peak_freq":
            return data.peak_freq
        if key == "peak_power":
            return data.peak_power
        if key == "tuner_type":
            return data.tuner_type
        if key == "serial":
            return data.serial or None
        return None

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data
        if data is None or self.entity_description.key != "rssi":
            return None
        return {
            ATTR_SPECTRUM_PEAK: data.peak_power,
            ATTR_SPECTRUM_PEAK_FREQ: data.peak_freq,
            ATTR_SPECTRUM_NOISE_FLOOR: data.noise_floor,
            "spectrum_bins": len(data.spectrum),
        }
