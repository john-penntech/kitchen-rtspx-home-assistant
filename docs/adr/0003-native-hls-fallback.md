# ADR 0003: Use the HA-managed go2rtc restream for HLS

- Status: Accepted
- Date: 2026-10-20
- Owner: `@john-penntech`

## Context

WebRTC may be unreachable from a dashboard client. Home Assistant also attempts
HLS, but the native PyAV stream worker cannot open the RTSPX scheme. A failed
HLS worker can mark an otherwise reachable camera unavailable. Generic Camera
adds another FFmpeg wrapper and does not resolve this protocol mismatch.

## Decision

Keep `stream_source()` returning the protected RTSPX source to the native
go2rtc provider. Override the camera's HLS stream creation to prepare the source
using that provider's snapshot method, then call Home Assistant's native
stream API to register an on-demand H.264/AAC variant of the existing loopback
RTSP restream on port 18554. Limit output to 1280 pixels wide; the
original camera stream remains intact. Call native `create_stream` with this
compatibility stream so clients lacking HEVC support receive H.264 video.
Reuse Home Assistant's go2rtc camera-identifier helper and stream preferences.
Serialize initial stream creation, reuse the resulting worker, and fail without
exposing credentials when the native provider is absent or cannot prepare it.

Declare go2rtc and stream dependencies. Require the tested Home Assistant
2026.8.1 API baseline and its managed go2rtc server. Keep the upstream protocol,
source validation, credential storage, and public entity identity intact.

## Consequences

Clients can receive authenticated HLS over the existing Home Assistant HTTP
connection. There is no custom transport, additional proxy/service, external
listener, or firewall change. Preparing the first HLS stream requests one native
snapshot. The loopback port and identifier helper are compatibility assumptions
along with the native provider's authenticated `_rest_client.streams.add`
adapter. The adapter is checked before use and credentials never leave it.
These interfaces must be checked during Home Assistant upgrades. Local tests prove control
flow and safe source selection; decoded live playback must be verified in HA.
