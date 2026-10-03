"""
Register the SDR++ panel in the Home Assistant sidebar.

This makes the SDR++ interface appear as a dedicated sidebar entry,
just like AdGuard Home or Studio Code Server.
"""
from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components import panel_custom
from homeassistant.core import HomeAssistant
from homeassistant.components.http import StaticPathConfig

_LOGGER = logging.getLogger(__name__)

PANEL_TITLE = "SDR++"
PANEL_ICON = "mdi:radio-tower"
PANEL_NAME = "sdrplusplus"


async def async_register_panel(hass: HomeAssistant) -> None:
    """Register the SDR++ sidebar panel."""
    try:
        # Serve panel.js from the integration's www directory
        panel_js_path = Path(__file__).parent / "www" / "panel.js"
        if panel_js_path.exists():
            await hass.http.async_register_static_paths([
                StaticPathConfig(
                    url_path="/rtl_dsr/panel.js",
                    path=str(panel_js_path),
                    cache_headers=True,
                )
            ])
            module_url = "/rtl_dsr/panel.js"
        else:
            # Fallback to www directory
            module_url = "/local/rtl_dsr/panel.js"

        await panel_custom.async_register_panel(
            hass,
            frontend_url_path=PANEL_NAME,
            webcomponent_name="sdr-plus-plus-panel",
            sidebar_title=PANEL_TITLE,
            sidebar_icon=PANEL_ICON,
            module_url=module_url,
            embed_iframe=True,
            require_admin=False,
            config={},
        )
        _LOGGER.info("SDR++ panel registered in sidebar")
    except Exception as exc:
        _LOGGER.error("Failed to register SDR++ panel: %s", exc)
