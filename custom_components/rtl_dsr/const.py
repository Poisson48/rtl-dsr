"""Constants for the RTL-SDR integration."""
from __future__ import annotations

from datetime import timedelta
from logging import Logger, getLogger

from homeassistant.const import Platform

DOMAIN = "rtl_dsr"
LOGGER: Logger = getLogger(__package__)

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.TEXT,
]

# How often the dongle is polled for status (MHz / dB / °C).
SCAN_INTERVAL = timedelta(seconds=30)

CONF_DEVICE_INDEX = "device_index"
CONF_SAMPLE_RATE = "sample_rate"
CONF_CENTER_FREQ = "center_freq"
CONF_GAIN = "gain"

# Values used when the RTL-SDR library is not installed (e.g. CI, dev boxes).
DEFAULT_DEVICE_INDEX = 0
DEFAULT_SAMPLE_RATE = 2.048  # MHz
DEFAULT_CENTER_FREQ = 100.0  # MHz (FM broadcast band — good smoke test)
DEFAULT_GAIN = "auto"

GAIN_VALUES = ["auto", "0.0", "0.9", "1.4", "2.7", "3.7", "7.7", "8.7",  # noqa: E501
              "12.5", "14.4", "15.7", "16.6", "19.7", "20.7", "22.9", "25.4",  # noqa: E501
              "28.0", "29.7", "32.8", "33.8", "36.4", "37.2", "38.6", "40.2",  # noqa: E501
              "42.1", "43.4", "43.9", "44.5", "48.0", "49.6"]

# Attribute keys
ATTR_FREQUENCY = "frequency"
ATTR_SAMPLE_RATE = "sample_rate"
ATTR_GAIN = "gain"
ATTR_MODE = "mode"
ATTR_PREAMP = "preamp"
ATTR_PPM = "ppm"
ATTR_BANDWIDTH = "bandwidth"
ATTR_TUNER_TYPE = "tuner_type"
ATTR_SERIAL = "serial"
ATTR_GAIN_STAGES = "gain_stages"

# Service names
SERVICE_SET_MODE = "set_mode"
SERVICE_SET_GAIN = "set_gain"
SERVICE_SET_PPM = "set_ppm"
SERVICE_SET_SAMPLE_RATE = "set_sample_rate"
SERVICE_SET_PREAMP = "set_preamp"
SERVICE_SET_BANDWIDTH = "set_bandwidth"
SERVICE_SET_FREQUENCY = "set_frequency"
SERVICE_SET_SQUELCH = "set_squelch"
SERVICE_RESET = "reset"
SERVICE_GET_FFT = "get_fft"

# Attribute keys used by the FFT service response
ATTR_FFT_DB = "bins"
ATTR_FFT_SIZE = "bin_count"
ATTR_CENTER_FREQ = "center_freq"
ATTR_PEAK_DB = "peak_db"
ATTR_PEAK_FREQ = "peak_freq"
ATTR_NOISE_FLOOR = "noise_floor"

# Mode values
MODE_OFF = "off"
MODE_SPECTRUM = "spectrum"
MODE_NFM = "nfm"
MODE_WFM = "wfm"
MODE_AM = "am"
MODE_USB = "usb"
MODE_LSB = "lsb"
MODE_RAW = "raw"
MODES = [MODE_OFF, MODE_SPECTRUM, MODE_NFM, MODE_WFM, MODE_AM, MODE_USB, MODE_LSB, MODE_RAW]  # noqa: E501

ATTR_SPECTRUM_PEAK = "spectrum_peak"
ATTR_SPECTRUM_PEAK_FREQ = "spectrum_peak_freq"
ATTR_SPECTRUM_NOISE_FLOOR = "spectrum_noise_floor"
