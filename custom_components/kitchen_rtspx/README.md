# RTSPX Camera Bridge

Install through HACS, restart Home Assistant, then add **RTSPX Camera Bridge**
from **Settings > Devices & services**. Add one config entry per camera.

The stream URL must use `rtspx://`, include a host and stream path, and omit the
`enableSrtp` query option. URLs are masked in the GUI and redacted from
diagnostics.

Version 1.1.4 uses Home Assistant's managed go2rtc loopback restream for native
H.264 HLS fallback when WebRTC or HEVC decoding is unavailable. The on-demand
compatibility stream is limited to 1280 pixels wide.
It requires Home Assistant 2026.8.1 or
later with its managed go2rtc server, and adds no proxy or external listener.

Legacy `camera: - platform: kitchen_rtspx` definitions are imported as GUI
config entries on the first v1.1.1 restart. Verify the imported entries, remove
the YAML block, run `ha core check`, and restart again.

Full installation, migration, and rollback instructions are maintained in the
[repository README](https://github.com/john-penntech/kitchen-rtspx-home-assistant).
