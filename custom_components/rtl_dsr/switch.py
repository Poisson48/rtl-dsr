"""Switch platform for the RTL-SDR integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import RtlDsrCoordinator
from .entity import RtlDsrEntity


@dataclass(frozen=True, kw_only=True)
class RtlDsrSwitchDescription(SwitchEntityDescription):
    """Switch description with dynamic value/setter hooks."""

    is_on_fn: Callable[[RtlDsrCoordinator], bool | None]
    set_fn: Callable[[RtlDsrCoordinator, bool], None]


SWITCHES: tuple[RtlDsrSwitchDescription, ...] = (
    RtlDsrSwitchDescription(
        key="preamp",
        translation_key="preamp",
        name="Preamp",
        icon="mdi:amplifier",
        entity_category=EntityCategory.CONFIG,
        is_on_fn=lambda c: c.preamp,
        set_fn=lambda c, v: c.set_preamp(v),
    ),
    RtlDsrSwitchDescription(
        key="reception",
        translation_key="reception",
        name="Reception",
        icon="mdi:radio-handheld",
        is_on_fn=lambda c: c.mode != "off",
        set_fn=lambda c, v: c.set_mode("spectrum" if v else "off"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: RtlDsrCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([RtlDsrSwitch(coordinator, d) for d in SWITCHES])


class RtlDsrSwitch(RtlDsrEntity, SwitchEntity):
    """Config switch (preamp) or the global reception on/off."""

    entity_description: RtlDsrSwitchDescription

    def __init__(
        self, coordinator: RtlDsrCoordinator, description: RtlDsrSwitchDescription
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        return self.entity_description.is_on_fn(self.coordinator)

    async def async_turn_on(self, **kwargs) -> None:
        await self.hass.async_add_executor_job(
            self.entity_description.set_fn, self.coordinator, True
        )

    async def async_turn_off(self, **kwargs) -> None:
        await self.hass.async_add_executor_job(
            self.entity_description.set_fn, self.coordinator, False
        )
