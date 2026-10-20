"""Exercise the real adapter with native HA interfaces stubbed; no hardware."""

from __future__ import annotations

import asyncio
import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch


COMPONENT = Path(__file__).resolve().parents[1] / "custom_components/kitchen_rtspx"


def load_camera_module():
    modules = {}

    def module(name, **attrs):
        value = ModuleType(name)
        value.__dict__.update(attrs)
        modules[name] = value
        return value

    class Schema:
        def __init__(self, *_args):
            pass

        def extend(self, *_args):
            return self

    class Camera:
        def __init__(self):
            self.hass = object()
            self.stream = None
            self.stream_options = {"rtsp_transport": "tcp"}
            self.webrtc_provider = None
            self.entity_id = "camera.front_dome"

        def async_write_ha_state(self):
            pass

    module("voluptuous", Schema=Schema, Required=lambda name: name,
           All=lambda *args: args)
    module("homeassistant")
    module("homeassistant.components")
    module("homeassistant.components.camera", PLATFORM_SCHEMA=Schema(),
           Camera=Camera, CameraEntityFeature=SimpleNamespace(STREAM=2),
           get_dynamic_camera_stream_settings=AsyncMock(return_value="native-prefs"))
    module("homeassistant.components.go2rtc")
    module("homeassistant.components.go2rtc.util",
           get_camera_identifier=lambda cam: f"kitchen_rtspx_{cam._attr_unique_id}")
    module("homeassistant.components.stream", Stream=object, create_stream=Mock())
    module("homeassistant.config_entries", SOURCE_IMPORT="import", ConfigEntry=object)
    module("homeassistant.const", CONF_NAME="name")
    module("homeassistant.core", HomeAssistant=object)
    module("homeassistant.exceptions", HomeAssistantError=RuntimeError)
    module("homeassistant.helpers")
    module("homeassistant.helpers.config_validation", string=str, ensure_list=list)
    module("homeassistant.helpers.device_registry", DeviceInfo=dict)
    module("homeassistant.helpers.entity_platform", AddEntitiesCallback=object)
    package = module("_rtspx_hls_test")
    package.__path__ = [str(COMPONENT)]
    spec = importlib.util.spec_from_file_location(
        "_rtspx_hls_test.camera", COMPONENT / "camera.py"
    )
    result = importlib.util.module_from_spec(spec)
    modules[spec.name] = result
    with patch.dict(sys.modules, modules):
        spec.loader.exec_module(result)
    return result


class HlsFallbackTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.module = load_camera_module()
        self.camera = self.module.KitchenRtspxCamera({
            "name": "Front Dome",
            "unique_id": "front_dome",
            "stream_source": "rtspx://camera.invalid:7441/PRIVATE_TEST_SOURCE",
        })
        self.provider = SimpleNamespace(
            domain="go2rtc", async_get_image=AsyncMock(return_value=b"jpeg"),
            _rest_client=SimpleNamespace(streams=SimpleNamespace(add=AsyncMock())),
        )
        self.camera.webrtc_provider = self.provider
        self.worker = SimpleNamespace(set_update_callback=Mock())
        self.module.create_stream.return_value = self.worker

    async def test_native_hls_uses_loopback_and_preserves_direct_rtspx(self):
        original = await self.camera.stream_source()
        result = await self.camera.async_create_stream()
        self.assertIs(result, self.worker)
        self.assertEqual(await self.camera.stream_source(), original)
        self.provider.async_get_image.assert_awaited_once_with(self.camera)
        self.module.create_stream.assert_called_once_with(
            self.camera.hass,
            "rtsp://127.0.0.1:18554/kitchen_rtspx_front_dome_hls_h264",
            options=self.camera.stream_options,
            dynamic_stream_settings="native-prefs",
            stream_label="camera.front_dome",
        )
        self.worker.set_update_callback.assert_called_once_with(
            self.camera.async_write_ha_state
        )
        self.assertNotIn("PRIVATE_TEST_SOURCE", self.module.create_stream.call_args.args[1])
        self.provider._rest_client.streams.add.assert_awaited_once_with(
            "kitchen_rtspx_front_dome_hls_h264",
            ["ffmpeg:rtsp://127.0.0.1:18554/kitchen_rtspx_front_dome"
             "#video=h264#audio=aac#width=1280"],
        )
        native_source = self.provider._rest_client.streams.add.call_args.args[1][0]
        self.assertNotRegex(native_source, r"\s", "go2rtc rejects source strings containing whitespace")

    async def test_simultaneous_requests_share_one_preparation_and_worker(self):
        async def prepare(_camera):
            await asyncio.sleep(0)
            return b"jpeg"

        self.provider.async_get_image.side_effect = prepare
        workers = await asyncio.gather(
            *(self.camera.async_create_stream() for _ in range(8))
        )
        self.assertTrue(all(worker is self.worker for worker in workers))
        self.provider.async_get_image.assert_awaited_once()
        self.module.create_stream.assert_called_once()
        self.provider._rest_client.streams.add.assert_awaited_once()

    async def test_unavailable_or_failing_native_stream_api_fails_safely(self):
        client = self.provider._rest_client
        self.provider._rest_client = None
        with self.assertRaisesRegex(RuntimeError, "restream API is unavailable"):
            await self.camera.async_create_stream()
        self.provider._rest_client = client
        client.streams.add.side_effect = RuntimeError("PRIVATE_TEST_SOURCE")
        with self.assertRaisesRegex(RuntimeError, "compatible camera restream") as failure:
            await self.camera.async_create_stream()
        self.assertNotIn("PRIVATE_TEST_SOURCE", str(failure.exception))
        self.assertTrue(failure.exception.__suppress_context__)
        self.module.create_stream.assert_not_called()

    async def test_missing_or_other_provider_never_passes_rtspx_to_hls(self):
        for provider in (None, SimpleNamespace(domain="other")):
            self.camera.webrtc_provider = provider
            with self.assertRaisesRegex(RuntimeError, "native go2rtc.*not ready"):
                await self.camera.async_create_stream()
        self.module.create_stream.assert_not_called()
        self.assertIsNone(self.camera.stream)

    async def test_failed_preparation_is_redacted_and_can_retry(self):
        self.provider.async_get_image.side_effect = RuntimeError(
            "rtspx://camera.invalid:7441/PRIVATE_TEST_SOURCE"
        )
        with self.assertRaisesRegex(RuntimeError, "Unable to prepare") as failure:
            await self.camera.async_create_stream()
        self.assertNotIn("PRIVATE_TEST_SOURCE", str(failure.exception))
        self.assertTrue(failure.exception.__suppress_context__)
        self.module.create_stream.assert_not_called()
        self.provider.async_get_image.side_effect = None
        self.provider.async_get_image.return_value = None
        with self.assertRaisesRegex(RuntimeError, "restream is not ready"):
            await self.camera.async_create_stream()
        self.assertIsNone(self.camera.stream)
        self.provider.async_get_image.return_value = b"jpeg"
        self.assertIs(await self.camera.async_create_stream(), self.worker)
