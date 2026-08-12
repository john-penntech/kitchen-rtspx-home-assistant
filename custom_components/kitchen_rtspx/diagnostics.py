"""Privacy-preserving diagnostics for RTSPX Camera Bridge."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_UNIQUE_ID


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return useful diagnostics without returning the credential-bearing URL."""
    return {
        "title": entry.title,
        "camera_id": entry.data[CONF_UNIQUE_ID],
        "stream_source": "REDACTED",
    }
