"""Number platform for the RTL-SDR integration."""
from __future__ import annotations

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfFrequency
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import RtlDsrCoordinator
from .entity import RtlDsrEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: RtlDsrCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            RtlDsrFrequencyNumber(coordinator),
            RtlDsrSampleRateNumber(coordinator),
            RtlDsrPpmNumber(coordinator),
            RtlDsrBandwidthNumber(coordinator),
            RtlDsrSquelchNumber(coordinator),
        ]
    )


class _RtlDsrNumberBase(RtlDsrEntity, NumberEntity):
    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator: RtlDsrCoordinator, key: str) -> None:
        super().__init__(coordinator, key)


class RtlDsrFrequencyNumber(_RtlDsrNumberBase):
    """Center frequency (MHz)."""

    _attr_name = "Frequency"
    _attr_translation_key = "frequency"
    _attr_native_unit_of_measurement = UnitOfFrequency.MEGAHERTZ
    _attr_device_class = NumberDeviceClass.FREQUENCY
    _attr_native_min_value = 24.0
    _attr_native_max_value = 1766.0
    _attr_native_step = 0.025

    def __init__(self, coordinator: RtlDsrCoordinator) -> None:
        super().__init__(coordinator, "frequency")

    @property
    def native_value(self) -> float | None:
        return self.coordinator.center_freq

    async def async_set_native_value(self, value: float) -> None:
        await self.hass.async_add_executor_job(self.coordinator.set_frequency, value)


class RtlDsrSampleRateNumber(_RtlDsrNumberBase):
    """Sample rate (MHz)."""

    _attr_name = "Sample rate"
    _attr_translation_key = "sample_rate"
    _attr_native_unit_of_measurement = UnitOfFrequency.MEGAHERTZ
    _attr_device_class = NumberDeviceClass.DATA_RATE
    _attr_native_min_value = 0.25
    _attr_native_max_value = 3.2
    _attr_native_step = 0.001
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: RtlDsrCoordinator) -> None:
        super().__init__(coordinator, "sample_rate")

    @property
    def native_value(self) -> float | None:
        return self.coordinator.sample_rate

    async def async_set_native_value(self, value: float) -> None:
        await self.hass.async_add_executor_job(self.coordinator.set_sample_rate, value)


class RtlDsrPpmNumber(_RtlDsrNumberBase):
    """Frequency correction (ppm)."""

    _attr_name = "Frequency correction"
    _attr_translation_key = "ppm"
    _attr_native_unit_of_measurement = "ppm"
    _attr_native_min_value = -150.0
    _attr_native_max_value = 150.0
    _attr_native_step = 1.0
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: RtlDsrCoordinator) -> None:
        super().__init__(coordinator, "ppm")

    @property
    def native_value(self) -> float | None:
        return float(self.coordinator.ppm)

    async def async_set_native_value(self, value: float) -> None:
        await self.hass.async_add_executor_job(self.coordinator.set_ppm, int(value))


class RtlDsrBandwidthNumber(_RtlDsrNumberBase):
    """IF bandwidth (MHz), 0 = auto."""

    _attr_name = "Bandwidth"
    _attr_translation_key = "bandwidth"
    _attr_native_unit_of_measurement = UnitOfFrequency.MEGAHERTZ
    _attr_native_min_value = 0.0
    _attr_native_max_value = 8.0
    _attr_native_step = 0.05
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: RtlDsrCoordinator) -> None:
        super().__init__(coordinator, "bandwidth")

    @property
    def native_value(self) -> float | None:
        return self.coordinator.bandwidth

    async def async_set_native_value(self, value: float) -> None:
        await self.hass.async_add_executor_job(self.coordinator.set_bandwidth, value)


class RtlDsrSquelchNumber(_RtlDsrNumberBase):
    """Squelch threshold in dB (for the 'signal detected' binary sensor)."""

    _attr_name = "Squelch"
    _attr_translation_key = "squelch"
    _attr_native_unit_of_measurement = "dB"
    _attr_native_min_value = -120.0
    _attr_native_max_value = 0.0
    _attr_native_step = 1.0
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: RtlDsrCoordinator) -> None:
        super().__init__(coordinator, "squelch")

    @property
    def native_value(self) -> float | None:
        return self.coordinator.squelch

    async def async_set_native_value(self, value: float) -> None:
        await self.hass.async_add_executor_job(self.coordinator.set_squelch, value)
