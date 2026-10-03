"""Models and helpers for the RTL-SDR integration."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .const import (
    ATTR_BANDWIDTH,
    ATTR_FREQUENCY,
    ATTR_GAIN,
    ATTR_MODE,
    ATTR_PREAMP,
    ATTR_PPM,
    ATTR_SAMPLE_RATE,
    MODE_OFF,
)


@dataclass
class SdrState:
    """Snapshot of the RTL-SDR device state."""

    connected: bool = False
    device_index: int = 0
    tuner_type: str = "unknown"
    serial: str = ""
    manufacturer: str = ""
    product: str = ""

    mode: str = MODE_OFF
    center_freq: float = 100.0  # MHz
    sample_rate: float = 2.048  # MHz
    gain: str | float = "auto"
    ppm: int = 0
    preamp: bool = False
    bandwidth: float = 0.0  # MHz (0 = auto)

    # Measurements
    rssi: float | None = None  # dB
    noise_floor: float | None = None  # dB
    peak_freq: float | None = None  # MHz
    peak_power: float | None = None  # dB
    spectrum: list[float] = field(default_factory=list)  # dB bins

    gain_stages: list[str] = field(default_factory=list)

    def as_attrs(self) -> dict[str, Any]:
        """Return the dict used for entity ``extra_state_attributes``."""
        return {
            ATTR_FREQUENCY: self.center_freq,
            ATTR_SAMPLE_RATE: self.sample_rate,
            ATTR_GAIN: self.gain,
            ATTR_MODE: self.mode,
            ATTR_PREAMP: self.preamp,
            ATTR_PPM: self.ppm,
            ATTR_BANDWIDTH: self.bandwidth,
        }


class SdrError(Exception):
    """Raised when a hardware operation fails."""


class Sdr:
    """Thin wrapper around :mod:`rtlsdr.RtlSdr`."""

    def __init__(self, device_index: int = 0) -> None:
        self._device_index = device_index
        self._sdr: Any = None
        self._tuner_type = "unknown"
        self._serial = ""
        self._manufacturer = ""
        self._product = ""
        self._gain_stages: list[str] = []

    def open(self) -> None:
        """Open the underlying RTL-SDR device."""
        try:
            from rtlsdr import RtlSdr
        except ImportError as exc:
            raise SdrError(
                "pyrtlsdr is not installed. Install the RTL-SDR add-on or "
                "run Home Assistant on a host with librtlsdr."
            ) from exc

        try:
            self._sdr = RtlSdr(device_index=self._device_index)
        except Exception as exc:
            raise SdrError(f"Cannot open RTL-SDR device {self._device_index}: {exc}") from exc

        try:
            self._tuner_type = str(self._sdr.get_tuner_type())
        except Exception:
            self._tuner_type = "unknown"
        try:
            self._serial = str(getattr(self._sdr, "serial", "") or "")
        except Exception:
            self._serial = ""
        try:
            self._gain_stages = list(self._sdr.get_gains() or [])
        except Exception:
            self._gain_stages = []

    def close(self) -> None:
        """Release the underlying device."""
        if self._sdr is None:
            return
        try:
            self._sdr.close()
        except Exception:
            pass
        self._sdr = None

    def set_center_freq(self, freq_mhz: float) -> None:
        if self._sdr is None:
            raise SdrError("Device is not open")
        self._sdr.center_freq = freq_mhz * 1e6

    def set_sample_rate(self, rate_mhz: float) -> None:
        if self._sdr is None:
            raise SdrError("Device is not open")
        self._sdr.sample_rate = rate_mhz * 1e6

    def set_gain(self, gain: str | float) -> None:
        if self._sdr is None:
            raise SdrError("Device is not open")
        if gain == "auto":
            self._sdr.gain = "auto"
        else:
            self._sdr.gain = float(gain)

    def set_freq_correction(self, ppm: int) -> None:
        if self._sdr is None:
            raise SdrError("Device is not open")
        self._sdr.freq_correction = int(ppm)

    def set_bandwidth(self, bw_mhz: float) -> None:
        if self._sdr is None:
            raise SdrError("Device is not open")
        try:
            self._sdr.set_bandwidth(bw_mhz * 1e6)
        except Exception:
            pass

    def read_rssi(self, samples: int = 256 * 1024) -> float:
        """Return an approximate RSSI in dBFS."""
        import math

        if self._sdr is None:
            raise SdrError("Device is not open")
        try:
            iq = self._sdr.read_samples(samples)
        except Exception as exc:
            raise SdrError(f"Read failed: {exc}") from exc

        power = 0.0
        for v in iq:
            power += (v.real * v.real) + (v.imag * v.imag)
        power /= max(1, len(iq))
        if power <= 0:
            return -120.0
        return 10.0 * math.log10(power)

    def read_spectrum(
        self, samples: int = 256 * 1024, bins: int = 64
    ) -> tuple[list[float], float, float, float]:
        """Return ``(bins_db, peak_freq_mhz, peak_db, noise_floor_db)``."""
        import math

        if bins > 64:
            samples = min(4 * 1024 * 1024, max(samples, bins * 512))
        if self._sdr is None:
            raise SdrError("Device is not open")
        try:
            iq = self._sdr.read_samples(samples)
        except Exception as exc:
            raise SdrError(f"Read failed: {exc}") from exc

        n = len(iq)
        if n == 0:
            return [], 0.0, -120.0, -120.0

        per_bin = max(1, n // bins)
        out: list[float] = []
        for b in range(bins):
            start = b * per_bin
            end = min(n, start + per_bin)
            p = 0.0
            for v in iq[start:end]:
                p += (v.real * v.real) + (v.imag * v.imag)
            cnt = max(1, end - start)
            p /= cnt
            out.append(10.0 * math.log10(p) if p > 0 else -120.0)

        peak_idx = max(range(len(out)), key=lambda i: out[i])
        peak_db = out[peak_idx]
        noise_floor = min(out)
        span = self._sample_rate_mhz() or 2.048
        center = self._center_freq_mhz() or 100.0
        peak_freq = center - span / 2 + (peak_idx + 0.5) * span / bins
        return out, peak_freq, peak_db, noise_floor

    def _center_freq_mhz(self) -> float:
        if self._sdr is None:
            return 0.0
        try:
            return float(self._sdr.center_freq) / 1e6
        except Exception:
            return 0.0

    def _sample_rate_mhz(self) -> float:
        if self._sdr is None:
            return 0.0
        try:
            return float(self._sdr.sample_rate) / 1e6
        except Exception:
            return 0.0

    def snapshot(self) -> SdrState:
        """Return a :class:`SdrState` describing the current device."""
        if self._sdr is None:
            return SdrState(connected=False, device_index=self._device_index)

        try:
            gain = self._sdr.gain
        except Exception:
            gain = "auto"
        return SdrState(
            connected=True,
            device_index=self._device_index,
            tuner_type=self._tuner_type,
            serial=self._serial,
            manufacturer=self._manufacturer,
            product=self._product,
            center_freq=self._center_freq_mhz(),
            sample_rate=self._sample_rate_mhz(),
            gain=gain,
            ppm=int(getattr(self._sdr, "freq_correction", 0) or 0),
            bandwidth=float(getattr(self._sdr, "bandwidth", 0) or 0) / 1e6,
            gain_stages=self._gain_stages,
        )


class MockSdr(Sdr):
    """Software stand-in used when ``pyrtlsdr`` is unavailable."""

    def __init__(self, device_index: int = 0) -> None:
        super().__init__(device_index)
        self._tuner_type = "R820T (mock)"
        self._serial = f"MOCK-{device_index:04d}"
        self._manufacturer = "Realtek"
        self._product = "RTL2838"
        self._gain_stages = ["LNA", "MIX", "VGA"]
        self._freq = 100.0
        self._rate = 2.048
        self._gain: str | float = "auto"
        self._ppm = 0
        self._bw = 0.0
        self._open = False

    def open(self) -> None:
        self._open = True

    def close(self) -> None:
        self._open = False

    def set_center_freq(self, freq_mhz: float) -> None:
        self._freq = freq_mhz

    def set_sample_rate(self, rate_mhz: float) -> None:
        self._rate = rate_mhz

    def set_gain(self, gain: str | float) -> None:
        self._gain = gain

    def set_freq_correction(self, ppm: int) -> None:
        self._ppm = ppm

    def set_bandwidth(self, bw_mhz: float) -> None:
        self._bw = bw_mhz

    def read_rssi(self, samples: int = 256 * 1024) -> float:
        return -42.5

    def read_spectrum(
        self, samples: int = 256 * 1024, bins: int = 64
    ) -> tuple[list[float], float, float, float]:
        import math

        out: list[float] = []
        for i in range(bins):
            base = -65.0 + 3.0 * math.sin(i / 5.0)
            if abs(i - bins // 3) < 2:
                base += 22.0
            if abs(i - 2 * bins // 3) < 1:
                base += 12.0
            out.append(base)
        peak_idx = max(range(len(out)), key=lambda i: out[i])
        peak_freq = self._freq - self._rate / 2 + (peak_idx + 0.5) * self._rate / bins
        return out, peak_freq, out[peak_idx], min(out)

    def _center_freq_mhz(self) -> float:
        return self._freq

    def _sample_rate_mhz(self) -> float:
        return self._rate

    def snapshot(self) -> SdrState:
        return SdrState(
            connected=self._open,
            device_index=self._device_index,
            tuner_type=self._tuner_type,
            serial=self._serial,
            manufacturer=self._manufacturer,
            product=self._product,
            mode="spectrum",
            center_freq=self._freq,
            sample_rate=self._rate,
            gain=self._gain,
            ppm=self._ppm,
            bandwidth=self._bw,
            rssi=-42.5,
            noise_floor=-60.0,
            peak_freq=self._freq + 0.2,
            peak_power=-53.0,
            spectrum=[-60.0 + (i % 7) for i in range(64)],
            gain_stages=self._gain_stages,
        )
