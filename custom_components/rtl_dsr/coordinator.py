"""DataUpdateCoordinator for the RTL-SDR integration."""
from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_CENTER_FREQ,
    CONF_DEVICE_INDEX,
    CONF_GAIN,
    CONF_SAMPLE_RATE,
    DEFAULT_CENTER_FREQ,
    DEFAULT_DEVICE_INDEX,
    DEFAULT_GAIN,
    DEFAULT_SAMPLE_RATE,
    DOMAIN,
    LOGGER,
    MODE_OFF,
    MODE_SPECTRUM,
    SCAN_INTERVAL,
)
from .model import MockSdr, Sdr, SdrError, SdrState


def _resolve_cls(name: str) -> type[Sdr]:
    return {"MockSdr": MockSdr}.get(name, Sdr)


class RtlDsrCoordinator(DataUpdateCoordinator[SdrState]):
    """Owns the :class:`Sdr` and exposes the latest :class:`SdrState`."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            LOGGER,
            name=f"{DOMAIN}-{entry.data[CONF_DEVICE_INDEX]}",
            update_interval=SCAN_INTERVAL,
        )
        self.entry = entry
        self._device_index: int = int(entry.data.get(CONF_DEVICE_INDEX, DEFAULT_DEVICE_INDEX))
        self._sdr_cls = _resolve_cls(entry.data.get("sdr_class", "Sdr"))
        self._sdr: Sdr | None = None

        opts = entry.options
        self._sample_rate: float = float(opts.get(CONF_SAMPLE_RATE, DEFAULT_SAMPLE_RATE))
        self._center_freq: float = float(opts.get(CONF_CENTER_FREQ, DEFAULT_CENTER_FREQ))
        self._gain: str | float = opts.get(CONF_GAIN, DEFAULT_GAIN)
        self._mode: str = MODE_SPECTRUM
        self._ppm: int = 0
        self._preamp: bool = False
        self._bandwidth: float = 0.0
        self._squelch: float = -90.0

    # ------------------------------------------------------------------
    # Device access
    # ------------------------------------------------------------------
    @property
    def sdr(self) -> Sdr | None:
        return self._sdr

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def center_freq(self) -> float:
        return self._center_freq

    @property
    def sample_rate(self) -> float:
        return self._sample_rate

    @property
    def gain(self) -> str | float:
        return self._gain

    @property
    def ppm(self) -> int:
        return self._ppm

    @property
    def preamp(self) -> bool:
        return self._preamp

    @property
    def bandwidth(self) -> float:
        return self._bandwidth

    @property
    def squelch(self) -> float:
        return self._squelch

    # ------------------------------------------------------------------
    def _ensure_open(self) -> Sdr:
        if self._sdr is None:
            self._sdr = self._sdr_cls(self._device_index)
            self._sdr.open()
            self._sdr.set_sample_rate(self._sample_rate)
            self._sdr.set_center_freq(self._center_freq)
            self._sdr.set_gain(self._gain)
            self._sdr.set_freq_correction(self._ppm)
            if self._bandwidth:
                self._sdr.set_bandwidth(self._bandwidth)
        return self._sdr

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def set_mode(self, mode: str) -> None:
        self._mode = mode
        self.hass.add_job(self.async_request_refresh)

    def set_frequency(self, freq_mhz: float) -> None:
        sdr = self._ensure_open()
        sdr.set_center_freq(freq_mhz)
        self._center_freq = freq_mhz
        self.hass.add_job(self.async_request_refresh)

    def set_sample_rate(self, rate_mhz: float) -> None:
        sdr = self._ensure_open()
        sdr.set_sample_rate(rate_mhz)
        self._sample_rate = rate_mhz
        self.hass.add_job(self.async_request_refresh)

    def set_gain(self, gain: str | float) -> None:
        sdr = self._ensure_open()
        sdr.set_gain(gain)
        self._gain = gain
        self.hass.add_job(self.async_request_refresh)

    def set_ppm(self, ppm: int) -> None:
        sdr = self._ensure_open()
        sdr.set_freq_correction(ppm)
        self._ppm = ppm
        self.hass.add_job(self.async_request_refresh)

    def set_preamp(self, enabled: bool) -> None:
        self._preamp = enabled
        self.hass.add_job(self.async_request_refresh)

    def set_bandwidth(self, bw_mhz: float) -> None:
        sdr = self._ensure_open()
        sdr.set_bandwidth(bw_mhz)
        self._bandwidth = bw_mhz
        self.hass.add_job(self.async_request_refresh)

    def set_squelch(self, level_db: float) -> None:
        self._squelch = level_db
        self.hass.add_job(self.async_request_refresh)

    @property
    def device_index(self) -> int:
        return self._device_index

    async def async_get_fft(self, bins: int = 512) -> SdrState:
        """Return a fresh :class:`SdrState` with ``spectrum`` set to ``bins``."""
        return await self.hass.async_add_executor_job(self._fft_sync, bins)

    def _fft_sync(self, bins: int) -> SdrState:
        try:
            sdr = self._ensure_open()
        except SdrError as exc:
            LOGGER.warning("RTL-SDR open failed for FFT, using MockSdr: %s", exc)
            self._sdr = MockSdr(self._device_index)
            self._sdr.open()
            sdr = self._sdr

        state = sdr.snapshot()
        state.mode = self._mode
        state.center_freq = self._center_freq
        state.sample_rate = self._sample_rate
        state.gain = self._gain
        state.ppm = self._ppm
        state.preamp = self._preamp
        state.bandwidth = self._bandwidth

        try:
            state.rssi = sdr.read_rssi()
            spec, peak_f, peak_p, noise = sdr.read_spectrum(bins=bins)
            state.spectrum = spec
            state.peak_freq = peak_f
            state.peak_power = peak_p
            state.noise_floor = noise
        except SdrError as exc:
            LOGGER.warning("RTL-SDR FFT failed: %s", exc)
            state.rssi = -120.0
            state.spectrum = [-120.0] * bins
            state.peak_freq = 0.0
            state.peak_power = -120.0
            state.noise_floor = -120.0

        return state

    def reset(self) -> None:
        self._mode = MODE_OFF
        self._center_freq = self.entry.options.get(CONF_CENTER_FREQ, DEFAULT_CENTER_FREQ)
        self._sample_rate = self.entry.options.get(CONF_SAMPLE_RATE, DEFAULT_SAMPLE_RATE)
        self._gain = self.entry.options.get(CONF_GAIN, DEFAULT_GAIN)
        self._ppm = 0
        self._preamp = False
        self._bandwidth = 0.0
        self.hass.add_job(self.async_request_refresh)

    # ------------------------------------------------------------------
    async def _async_update_data(self) -> SdrState:
        return await self.hass.async_add_executor_job(self._update_sync)

    def _update_sync(self) -> SdrState:
        try:
            sdr = self._ensure_open()
        except SdrError as exc:
            LOGGER.warning("RTL-SDR open failed, using MockSdr: %s", exc)
            self._sdr = MockSdr(self._device_index)
            self._sdr.open()
            sdr = self._sdr

        state = sdr.snapshot()
        state.mode = self._mode
        state.center_freq = self._center_freq
        state.sample_rate = self._sample_rate
        state.gain = self._gain
        state.ppm = self._ppm
        state.preamp = self._preamp
        state.bandwidth = self._bandwidth

        if self._mode != MODE_OFF:
            try:
                state.rssi = sdr.read_rssi()
                bins, peak_f, peak_p, noise = sdr.read_spectrum()
                state.spectrum = bins
                state.peak_freq = peak_f
                state.peak_power = peak_p
                state.noise_floor = noise
            except SdrError as exc:
                LOGGER.warning("RTL-SDR measurement failed: %s", exc)
                state.rssi = -120.0
                state.spectrum = []
                state.peak_freq = 0.0
                state.peak_power = -120.0
                state.noise_floor = -120.0
        else:
            state.rssi = None
            state.spectrum = []
            state.peak_freq = None
            state.peak_power = None
            state.noise_floor = None

        return state

    async def async_shutdown(self) -> None:
        """Close the device when the entry unloads."""
        if self._sdr is not None:
            await self.hass.async_add_executor_job(self._sdr.close)
            self._sdr = None
