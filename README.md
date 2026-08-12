# Kitchen RTSPX for Home Assistant

`kitchen_rtspx` is a small YAML camera platform that hands UniFi Protect secure
RTSP links directly to Home Assistant's built-in go2rtc provider. It uses
`rtspx://` without Protect's `?enableSrtp` suffix so Home Assistant does not
route the stream through FFmpeg.

This repository establishes source ownership and reproducible history for the
version 1.0.0 component deployed on the owner's local Home Assistant instance.
The four files in `custom_components/kitchen_rtspx/` are the exact deployed
snapshot; their SHA-256 values are recorded in `SHA256SUMS` and
`PROVENANCE.md`.

## Configuration

Copy `custom_components/kitchen_rtspx` into Home Assistant's
`/config/custom_components/` directory. Keep the actual stream URL in
`secrets.yaml`:

```yaml
camera:
  - platform: kitchen_rtspx
    cameras:
      - name: Grill Camera
        unique_id: kitchen_grill_camera
        stream_source: !secret kitchen_grill_rtspx
```

The secret should contain the local `rtspx://` source. Never commit it.

After installation, run `ha core check` before restarting Home Assistant.
Runtime installation and restart are intentionally separate from this source
repository.

## Verification

The test suite uses only the Python standard library:

```text
python -m compileall -q custom_components tests
python -m unittest discover -s tests -v
```

The checks verify the deployed snapshot hashes, manifest, YAML-platform schema
contract, and absence of high-risk execution or write primitives.

## Design and recovery

- [Architecture decision](docs/adr/0001-native-go2rtc-rtspx-camera-platform.md)
- [Provenance](PROVENANCE.md)
- [Rollback](ROLLBACK.md)
- [Security policy](SECURITY.md)

This is an independent local integration, not an official Home Assistant or
Ubiquiti project.
