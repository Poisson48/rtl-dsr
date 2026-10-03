"""Button platform for the RTL-SDR integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import RtlDsrCoordinator
from .entity import RtlDsrEntity


@dataclass(frozen=True, kw_only=True)
class RtlDsrButtonDescription(ButtonEntityDescription):
    """Button description with a bound action."""

    action_fn: Callable[[RtlDsrCoordinator], None]


BUTTONS: tuple[RtlDsrButtonDescription, ...] = (
    RtlDsrButtonDescription(
        key="reset",
        translation_key="reset",
        name="Reset",
        icon="mdi:restore",
        entity_category=EntityCategory.CONFIG,
        action_fn=lambda c: c.reset(),
    ),
    RtlDsrButtonDescription(
        key="scan_fm",
        translation_key="scan_fm",
        name="Scan FM band",
        icon="mdi:radio",
        action_fn=lambda c: (
            c.set_frequency(87.6),
            c.set_sample_rate(2.048),
            c.set_mode("wfm"),
        ),
    ),
    RtlDsrButtonDescription(
        key="scan_ism_433",
        translation_key="scan_ism_433",
        name="Scan ISM 433 MHz",
        icon="mdi:antenna",
        action_fn=lambda c: (
            c.set_frequency(433.92),
            c.set_sample_rate(1.024),
            c.set_mode("nfm"),
        ),
    ),
    RtlDsrButtonDescription(
        key="scan_ism_868",
        translation_key="scan_ism_868",
        name="Scan ISM 868 MHz",
        icon="mdi:antenna",
        action_fn=lambda c: (
            c.set_frequency(868.3),
            c.set_sample_rate(1.024),
            c.set_mode("nfm"),
        ),
    ),
    RtlDsrButtonDescription(
        key="scan_adsb",
        translation_key="scan_adsb",
        name="Scan ADS-B 1090 MHz",
        icon="mdi:airplane",
        action_fn=lambda c: (
            c.set_frequency(1090.0),
            c.set_sample_rate(2.4),
            c.set_mode("raw"),
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: RtlDsrCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([RtlDsrButton(coordinator, d) for d in BUTTONS])


class RtlDsrButton(RtlDsrEntity, ButtonEntity):
    """Trigger a preset scan / reset."""

    entity_description: RtlDsrButtonDescription

    def __init__(
        self, coordinator: RtlDsrCoordinator, description: RtlDsrButtonDescription
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    async def async_press(self) -> None:
        await self.hass.async_add_executor_job(
            self.entity_description.action_fn, self.coordinator
        )
