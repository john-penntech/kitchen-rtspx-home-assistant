# Kitchen RTSPX cameras

This YAML camera platform exposes UniFi Protect secure RTSP links directly to
Home Assistant's built-in go2rtc provider. It intentionally uses `rtspx://` and
omits Protect's `?enableSrtp` suffix so the stream is handled by go2rtc instead
of FFmpeg.

Keep real stream links in Home Assistant `secrets.yaml`; do not commit them.

```yaml
camera:
  - platform: kitchen_rtspx
    cameras:
      - name: Grill Camera
        unique_id: kitchen_grill_camera
        stream_source: !secret kitchen_grill_rtspx
```
