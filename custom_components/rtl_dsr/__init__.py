"""The RTL-SDR integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN, LOGGER, PLATFORMS
from .coordinator import RtlDsrCoordinator
from .services import async_setup_services, async_unload_services
from .websocket_api import async_setup_fft_service, async_unload_fft_service
from .panel import async_register_panel


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up RTL-SDR from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    coordinator = RtlDsrCoordinator(hass, entry)
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as exc:  # noqa: BLE001
        LOGGER.error("RTL-SDR initialisation failed: %s", exc)
        return False

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await async_setup_services(hass)
    await async_setup_fft_service(hass)
    await async_register_panel(hass)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator: RtlDsrCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_shutdown()
        if not hass.data[DOMAIN]:
            await async_unload_services(hass)
            await async_unload_fft_service(hass)
    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)
