"""
Register the SDR++ panel in the Home Assistant sidebar.

This makes the SDR++ interface appear as a dedicated sidebar entry,
just like AdGuard Home or Studio Code Server.
"""
from __future__ import annotations

import logging

from homeassistant.components import panel_custom
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

PANEL_URL = "/api/rtl_dsr/static/sdrplusplus.html"
PANEL_TITLE = "SDR++"
PANEL_ICON = "mdi:radio-tower"
PANEL_NAME = "sdrplusplus"


async def async_register_panel(hass: HomeAssistant) -> None:
    """Register the SDR++ sidebar panel."""
    try:
        await panel_custom.async_register_panel(
            hass,
            frontend_url_path=PANEL_NAME,
            webcomponent_name="sdr-plus-plus-panel",
            sidebar_title=PANEL_TITLE,
            sidebar_icon=PANEL_ICON,
            module_url="/local/rtl_dsr/panel.js",
            embed_iframe=True,
            require_admin=False,
            config={},
        )
        _LOGGER.info("SDR++ panel registered in sidebar")
    except Exception as exc:
        _LOGGER.error("Failed to register SDR++ panel: %s", exc)
