"""Expose RTSPX sources directly to Home Assistant's native go2rtc provider."""

from __future__ import annotations

import asyncio
from typing import Any

import voluptuous as vol

from homeassistant.components.camera import (
    PLATFORM_SCHEMA,
    Camera,
    CameraEntityFeature,
    get_dynamic_camera_stream_settings,
)
from homeassistant.components.go2rtc.util import get_camera_identifier
from homeassistant.components.stream import Stream, create_stream
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_STREAM_SOURCE, CONF_UNIQUE_ID, DOMAIN, validate_rtspx_url

CONF_CAMERAS = "cameras"

CAMERA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_UNIQUE_ID): cv.string,
        vol.Required(CONF_STREAM_SOURCE): vol.All(cv.string, validate_rtspx_url),
    }
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {vol.Required(CONF_CAMERAS): vol.All(cv.ensure_list, [CAMERA_SCHEMA])}
)


class KitchenRtspxCamera(Camera):
    """A camera source consumed directly by the native go2rtc integration."""

    _attr_supported_features = CameraEntityFeature.STREAM
    _attr_should_poll = False

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__()
        self._attr_name = config[CONF_NAME]
        self._attr_unique_id = config[CONF_UNIQUE_ID]
        self._stream_source = config[CONF_STREAM_SOURCE]
        self._hls_stream_lock = asyncio.Lock()

    @property
    def device_info(self) -> DeviceInfo:
        """Group the camera as a device in Home Assistant."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._attr_unique_id)},
            name=self._attr_name,
            manufacturer="RTSPX Camera Bridge",
            model="Native go2rtc stream",
        )

    @property
    def use_stream_for_stills(self) -> bool:
        """Use go2rtc to generate still images from the stream."""
        return True

    async def stream_source(self) -> str | None:
        """Return the RTSPX source without routing it through FFmpeg."""
        return self._stream_source

    async def async_create_stream(self) -> Stream | None:
        """Give native HLS a local go2rtc restream, never an RTSPX URL.

        PyAV cannot open rtspx. WebRTC still consumes stream_source directly;
        HLS uses an H.264 compatibility stream on go2rtc's loopback RTSP port.
        """
        async with self._hls_stream_lock:
            if self.stream is not None:
                return self.stream
            provider = self.webrtc_provider
            if provider is None or provider.domain != "go2rtc":
                raise HomeAssistantError("The native go2rtc camera provider is not ready")
            try:
                # The public provider method registers this camera's source in
                # go2rtc and verifies it without exposing a stream credential.
                image = await provider.async_get_image(self)
            except Exception:
                raise HomeAssistantError("Unable to prepare the native camera restream") from None
            if image is None:
                raise HomeAssistantError("The native camera restream is not ready")
            identifier = get_camera_identifier(self)
            hls_identifier = f"{identifier}_hls_h264"
            # HA's provider already owns this authenticated native client. Keep
            # the compatibility stream entirely inside the managed server.
            client = getattr(provider, "_rest_client", None)
            if client is None:
                raise HomeAssistantError("The native go2rtc restream API is unavailable")
            try:
                await client.streams.add(
                    hls_identifier,
                    [
                        f"ffmpeg:rtsp://127.0.0.1:18554/{identifier}"
                        "#video=h264#audio=aac#width=1280"
                    ],
                )
            except Exception:
                raise HomeAssistantError("Unable to prepare the compatible camera restream") from None
            self.stream = create_stream(
                self.hass,
                f"rtsp://127.0.0.1:18554/{hls_identifier}",
                options=self.stream_options,
                dynamic_stream_settings=await get_dynamic_camera_stream_settings(
                    self.hass, self.entity_id
                ),
                stream_label=self.entity_id,
            )
            self.stream.set_update_callback(self.async_write_ha_state)
            return self.stream

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
    """Import legacy YAML cameras as normal Home Assistant config entries."""
    for item in config[CONF_CAMERAS]:
        await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_IMPORT},
            data=dict(item),
        )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up one camera from the Home Assistant GUI."""
    async_add_entities([KitchenRtspxCamera(dict(entry.data))])
