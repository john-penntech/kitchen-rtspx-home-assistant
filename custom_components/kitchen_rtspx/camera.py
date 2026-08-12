"""Expose secure UniFi RTSP sources directly to Home Assistant's go2rtc provider."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components.camera import (
    PLATFORM_SCHEMA,
    Camera,
    CameraEntityFeature,
)
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback


CONF_CAMERAS = "cameras"
CONF_STREAM_SOURCE = "stream_source"
CONF_UNIQUE_ID = "unique_id"

CAMERA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_UNIQUE_ID): cv.string,
        vol.Required(CONF_STREAM_SOURCE): cv.string,
    }
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {vol.Required(CONF_CAMERAS): vol.All(cv.ensure_list, [CAMERA_SCHEMA])}
)


class KitchenRtspxCamera(Camera):
    """A camera source consumed directly by the native go2rtc integration."""

    _attr_supported_features = CameraEntityFeature.STREAM

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__()
        self._attr_name = config[CONF_NAME]
        self._attr_unique_id = config[CONF_UNIQUE_ID]
        self._stream_source = config[CONF_STREAM_SOURCE]

    @property
    def use_stream_for_stills(self) -> bool:
        """Use go2rtc to generate still images from the stream."""
        return True

    async def stream_source(self) -> str | None:
        """Return the RTSPX source without routing it through FFmpeg."""
        return self._stream_source

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Defer still generation to Home Assistant's camera provider."""
        return None


async def async_setup_platform(
    hass: HomeAssistant,
    config: dict[str, Any],
    async_add_entities: AddEntitiesCallback,
    discovery_info: dict[str, Any] | None = None,
) -> None:
    """Set up configured kitchen cameras."""
    async_add_entities(KitchenRtspxCamera(item) for item in config[CONF_CAMERAS])
