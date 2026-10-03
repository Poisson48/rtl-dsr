"""Websocket / service helpers exposing FFT data for the SDR++ card.

The custom panel card cannot talk to the RTL-SDR hardware directly; it
asks the Home Assistant backend through the ``rtl_dsr.get_fft`` service,
which returns a compact JSON payload: an array of dB bins plus the span
and center frequency so the card can label the axis.
"""
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

from .const import (
    ATTR_CENTER_FREQ,
    ATTR_FFT_DB,
    ATTR_FFT_SIZE,
    ATTR_NOISE_FLOOR,
    ATTR_PEAK_DB,
    ATTR_PEAK_FREQ,
    ATTR_SAMPLE_RATE,
    DOMAIN,
    LOGGER,
    MODE_OFF,
    SERVICE_GET_FFT,
)
from .coordinator import RtlDsrCoordinator
from .model import SdrError


async def async_setup_fft_service(hass: HomeAssistant) -> None:
    """Register ``rtl_dsr.get_fft`` (returns one measurement snapshot)."""
    if hass.services.has_service(DOMAIN, SERVICE_GET_FFT):
        return

    async def _handle_get_fft(call: ServiceCall) -> ServiceResponse:
        target = call.data.get("entry_id") or call.data.get("device_id")
        coord = _pick_coordinator(hass, target)
        if coord is None:
            return {"error": "no_device", "bins": []}
        try:
            state = await coord.async_get_fft()
        except SdrError as exc:
            LOGGER.warning("FFT service failed: %s", exc)
            return {"error": str(exc), "bins": []}
        return {
            "bins": state.spectrum,
            "bin_count": len(state.spectrum),
            "center_freq": state.center_freq,
            "sample_rate": state.sample_rate,
            "peak_freq": state.peak_freq,
            "peak_db": state.peak_power,
            "noise_floor": state.noise_floor,
            "rssi": state.rssi,
            "tuner_type": state.tuner_type,
            "mode": state.mode,
            "gain": state.gain,
        }

    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_FFT,
        _handle_get_fft,
        schema=vol.Schema(
            {
                vol.Optional("entry_id"): cv.string,
                vol.Optional("device_id"): cv.string,
                vol.Optional("fft_size", default=512): vol.All(
                    vol.Coerce(int), vol.Range(min=64, max=4096)
                ),
            }
        ),
        supports_response=SupportsResponse.OPTIONAL,
    )


def _pick_coordinator(hass: HomeAssistant, target: str | None) -> RtlDsrCoordinator | None:
    """Return the first coordinator matching ``target`` (or the first one)."""
    all_c: list[RtlDsrCoordinator] = list(hass.data.get(DOMAIN, {}).values())
    if not all_c:
        return None
    if target:
        for c in all_c:
            if c.entry.entry_id == target or f"rtl_dsr_{c.device_index}" == target:
                return c
    return all_c[0]


async def async_unload_fft_service(hass: HomeAssistant) -> None:
    if hass.services.has_service(DOMAIN, SERVICE_GET_FFT):
        hass.services.async_remove(DOMAIN, SERVICE_GET_FFT)
