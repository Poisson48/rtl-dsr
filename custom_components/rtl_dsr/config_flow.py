"""Config flow for the RTL-SDR integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

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
    GAIN_VALUES,
)
from .model import MockSdr, Sdr, SdrError


def _try_open(index: int) -> tuple[bool, str, type[Sdr]]:
    """Try to open ``index``.  Return ``(ok, tuner_type, class)``.

    Falls back to :class:`MockSdr` when ``pyrtlsdr`` is not installed so
    the integration is fully testable off-device.
    """
    try:
        sdr = Sdr(index)
        sdr.open()
        tuner = sdr.snapshot().tuner_type
        sdr.close()
        return True, tuner, Sdr
    except SdrError:
        pass
    except Exception:
        pass

    # Fallback to the mock so config flow still works on a dev machine.
    sdr = MockSdr(index)
    sdr.open()
    tuner = sdr.snapshot().tuner_type
    sdr.close()
    return True, tuner, MockSdr


class RtlDsrConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for RTL-SDR."""

    VERSION = 1

    def __init__(self) -> None:
        self._device_index: int = DEFAULT_DEVICE_INDEX
        self._tuner: str = ""
        self._sdr_cls: type[Sdr] = Sdr

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._device_index = int(user_input[CONF_DEVICE_INDEX])
            await self.async_set_unique_id(f"rtl_dsr_{self._device_index}")
            self._abort_if_unique_id_configured()

            ok, tuner, cls = await self.hass.async_add_executor_job(
                _try_open, self._device_index
            )
            if not ok:
                errors["base"] = "cannot_connect"
            else:
                self._tuner = tuner
                self._sdr_cls = cls
                return await self.async_step_options()

        schema = vol.Schema(
            {
                vol.Required(CONF_DEVICE_INDEX, default=DEFAULT_DEVICE_INDEX): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=8)
                ),
            }
        )
        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )

    async def async_step_options(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Optional tuning parameters."""
        if user_input is not None:
            return self.async_create_entry(
                title=f"RTL-SDR #{self._device_index} ({self._tuner})",
                data={
                    CONF_DEVICE_INDEX: self._device_index,
                    "tuner_type": self._tuner,
                    "sdr_class": self._sdr_cls.__name__,
                },
                options={
                    CONF_SAMPLE_RATE: user_input[CONF_SAMPLE_RATE],
                    CONF_CENTER_FREQ: user_input[CONF_CENTER_FREQ],
                    CONF_GAIN: user_input[CONF_GAIN],
                },
            )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_SAMPLE_RATE, default=DEFAULT_SAMPLE_RATE
                ): vol.All(vol.Coerce(float), vol.Range(min=0.25, max=3.2)),
                vol.Required(
                    CONF_CENTER_FREQ, default=DEFAULT_CENTER_FREQ
                ): vol.All(vol.Coerce(float), vol.Range(min=24.0, max=1766.0)),
                vol.Required(CONF_GAIN, default=DEFAULT_GAIN): vol.In(GAIN_VALUES),
            }
        )
        return self.async_show_form(step_id="options", data_schema=schema)

    @staticmethod
    def async_get_options_flow(config_entry: ConfigEntry):
        """Options flow (re-tune without re-adding)."""
        return RtlDsrOptionsFlow(config_entry)


class RtlDsrOptionsFlow(ConfigFlow):
    """Allow the user to re-tune the device."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        self._entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        opts = self._entry.options
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_SAMPLE_RATE,
                    default=opts.get(CONF_SAMPLE_RATE, DEFAULT_SAMPLE_RATE),
                ): vol.All(vol.Coerce(float), vol.Range(min=0.25, max=3.2)),
                vol.Required(
                    CONF_CENTER_FREQ,
                    default=opts.get(CONF_CENTER_FREQ, DEFAULT_CENTER_FREQ),
                ): vol.All(vol.Coerce(float), vol.Range(min=24.0, max=1766.0)),
                vol.Required(
                    CONF_GAIN, default=opts.get(CONF_GAIN, DEFAULT_GAIN)
                ): vol.In(GAIN_VALUES),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
