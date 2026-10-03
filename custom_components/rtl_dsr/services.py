"""Services for the RTL-SDR integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr

from .const import (
    ATTR_BANDWIDTH,
    ATTR_FREQUENCY,
    ATTR_GAIN,
    ATTR_MODE,
    ATTR_PREAMP,
    ATTR_PPM,
    ATTR_SAMPLE_RATE,
    DOMAIN,
    LOGGER,
    MODES,
    SERVICE_RESET,
    SERVICE_SET_BANDWIDTH,
    SERVICE_SET_FREQUENCY,
    SERVICE_SET_GAIN,
    SERVICE_SET_MODE,
    SERVICE_SET_PREAMP,
    SERVICE_SET_PPM,
    SERVICE_SET_SAMPLE_RATE,
    SERVICE_SET_SQUELCH,
)
from .coordinator import RtlDsrCoordinator
from .model import SdrError

# Base schema for targeting a specific device (as a dict, not vol.Schema)
SERVICE_TARGET_FIELDS = {
    vol.Optional("device_id"): cv.string,
    vol.Optional("entry_id"): cv.string,
}


def _find_coordinators(
    hass: HomeAssistant, call: ServiceCall
) -> list[RtlDsrCoordinator]:
    all_c: list[RtlDsrCoordinator] = list(hass.data.get(DOMAIN, {}).values())
    if not all_c:
        return []
    entry_id = call.data.get("entry_id")
    device_id = call.data.get("device_id")
    if entry_id:
        return [c for c in all_c if c.entry.entry_id == entry_id]
    if device_id:
        registry = dr.async_get(hass)
        device = registry.async_get(device_id)
        if device is None:
            return []
        wanted = {i[1] for i in device.identifiers if i[0] == DOMAIN}
        out = []
        for c in all_c:
            idx = getattr(c, "_device_index", None)
            if f"rtl_dsr_{idx}" in wanted:
                out.append(c)
        return out
    return all_c


async def async_setup_services(hass: HomeAssistant) -> None:
    """Register services once."""
    if hass.services.has_service(DOMAIN, SERVICE_SET_FREQUENCY):
        return

    async def _handle_set_frequency(call: ServiceCall) -> None:
        freq = float(call.data[ATTR_FREQUENCY])
        for c in _find_coordinators(hass, call):
            await hass.async_add_executor_job(c.set_frequency, freq)

    async def _handle_set_sample_rate(call: ServiceCall) -> None:
        rate = float(call.data[ATTR_SAMPLE_RATE])
        for c in _find_coordinators(hass, call):
            await hass.async_add_executor_job(c.set_sample_rate, rate)

    async def _handle_set_gain(call: ServiceCall) -> None:
        raw = call.data[ATTR_GAIN]
        gain: str | float = raw
        if raw != "auto":
            try:
                gain = float(raw)
            except (TypeError, ValueError):
                gain = raw
        for c in _find_coordinators(hass, call):
            await hass.async_add_executor_job(c.set_gain, gain)

    async def _handle_set_ppm(call: ServiceCall) -> None:
        ppm = int(call.data[ATTR_PPM])
        for c in _find_coordinators(hass, call):
            await hass.async_add_executor_job(c.set_ppm, ppm)

    async def _handle_set_mode(call: ServiceCall) -> None:
        mode = call.data[ATTR_MODE]
        if mode not in MODES:
            LOGGER.error("Unknown mode %s", mode)
            return
        for c in _find_coordinators(hass, call):
            await hass.async_add_executor_job(c.set_mode, mode)

    async def _handle_set_preamp(call: ServiceCall) -> None:
        enabled = bool(call.data[ATTR_PREAMP])
        for c in _find_coordinators(hass, call):
            await hass.async_add_executor_job(c.set_preamp, enabled)

    async def _handle_set_bandwidth(call: ServiceCall) -> None:
        bw = float(call.data[ATTR_BANDWIDTH])
        for c in _find_coordinators(hass, call):
            await hass.async_add_executor_job(c.set_bandwidth, bw)

    async def _handle_set_squelch(call: ServiceCall) -> None:
        level = float(call.data["level"])
        for c in _find_coordinators(hass, call):
            await hass.async_add_executor_job(c.set_squelch, level)

    async def _handle_reset(call: ServiceCall) -> None:
        for c in _find_coordinators(hass, call):
            await hass.async_add_executor_job(c.reset)

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_FREQUENCY,
        _handle_set_frequency,
        schema=vol.Schema({vol.Required(ATTR_FREQUENCY): vol.Coerce(float), **SERVICE_TARGET_FIELDS}),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_SAMPLE_RATE,
        _handle_set_sample_rate,
        schema=vol.Schema({vol.Required(ATTR_SAMPLE_RATE): vol.Coerce(float), **SERVICE_TARGET_FIELDS}),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_GAIN,
        _handle_set_gain,
        schema=vol.Schema({vol.Required(ATTR_GAIN): cv.string, **SERVICE_TARGET_FIELDS}),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_PPM,
        _handle_set_ppm,
        schema=vol.Schema({vol.Required(ATTR_PPM): vol.Coerce(int), **SERVICE_TARGET_FIELDS}),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_MODE,
        _handle_set_mode,
        schema=vol.Schema({vol.Required(ATTR_MODE): vol.In(MODES), **SERVICE_TARGET_FIELDS}),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_PREAMP,
        _handle_set_preamp,
        schema=vol.Schema({vol.Required(ATTR_PREAMP): cv.boolean, **SERVICE_TARGET_FIELDS}),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_BANDWIDTH,
        _handle_set_bandwidth,
        schema=vol.Schema({vol.Required(ATTR_BANDWIDTH): vol.Coerce(float), **SERVICE_TARGET_FIELDS}),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_SQUELCH,
        _handle_set_squelch,
        schema=vol.Schema({vol.Required("level"): vol.Coerce(float), **SERVICE_TARGET_FIELDS}),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_RESET,
        _handle_reset,
        schema=vol.Schema(SERVICE_TARGET_FIELDS),
    )


async def async_unload_services(hass: HomeAssistant) -> None:
    for name in (
        SERVICE_SET_FREQUENCY,
        SERVICE_SET_SAMPLE_RATE,
        SERVICE_SET_GAIN,
        SERVICE_SET_PPM,
        SERVICE_SET_MODE,
        SERVICE_SET_PREAMP,
        SERVICE_SET_BANDWIDTH,
        SERVICE_SET_SQUELCH,
        SERVICE_RESET,
    ):
        if hass.services.has_service(DOMAIN, name):
            hass.services.async_remove(DOMAIN, name)
