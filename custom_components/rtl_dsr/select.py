"""Select platform for the RTL-SDR integration."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, GAIN_VALUES, MODES
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
            RtlDsrModeSelect(coordinator),
            RtlDsrGainSelect(coordinator),
        ]
    )


class RtlDsrModeSelect(RtlDsrEntity, SelectEntity):
    """Choose the reception mode (demodulator)."""

    _attr_name = "Mode"
    _attr_translation_key = "mode"
    _attr_icon = "mdi:radio-tower"

    def __init__(self, coordinator: RtlDsrCoordinator) -> None:
        super().__init__(coordinator, "mode")

    @property
    def options(self) -> list[str]:
        return list(MODES)

    @property
    def current_option(self) -> str | None:
        return self.coordinator.mode

    async def async_select_option(self, option: str) -> None:
        await self.hass.async_add_executor_job(self.coordinator.set_mode, option)


class RtlDsrGainSelect(RtlDsrEntity, SelectEntity):
    """Tuner gain (auto or manual)."""

    _attr_name = "Gain"
    _attr_translation_key = "gain"
    _attr_icon = "mdi:volume-high"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: RtlDsrCoordinator) -> None:
        super().__init__(coordinator, "gain")

    @property
    def options(self) -> list[str]:
        return list(GAIN_VALUES)

    @property
    def current_option(self) -> str | None:
        return str(self.coordinator.gain)

    async def async_select_option(self, option: str) -> None:
        value: str | float = option
        if option != "auto":
            try:
                value = float(option)
            except ValueError:
                value = option
        await self.hass.async_add_executor_job(self.coordinator.set_gain, value)
