"""Text platform for the RTL-SDR integration (frequency entry as text)."""
from __future__ import annotations

from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
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
    async_add_entities([RtlDsrFrequencyText(coordinator)])


class RtlDsrFrequencyText(RtlDsrEntity, TextEntity):
    """Type a frequency like ``101.1`` or ``433.92`` directly."""

    _attr_name = "Set frequency (MHz)"
    _attr_translation_key = "set_frequency_text"
    _attr_pattern = r"^\d{2,4}(\.\d{1,6})?$"
    _attr_native_min = 4
    _attr_native_max = 10
    _attr_entity_category = EntityCategory.CONFIG
    _attr_icon = "mdi:digital-ocean"  # placeholder, replaced below

    def __init__(self, coordinator: RtlDsrCoordinator) -> None:
        super().__init__(coordinator, "set_frequency_text")
        self._attr_icon = "mdi:tune-vertical"

    @property
    def native_value(self) -> str | None:
        return f"{self.coordinator.center_freq:.3f}"

    async def async_set_value(self, value: str) -> None:
        try:
            freq = float(value)
        except ValueError:
            return
        await self.hass.async_add_executor_job(self.coordinator.set_frequency, freq)
