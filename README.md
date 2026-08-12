# RTSPX Camera Bridge for Home Assistant

[![Test](https://github.com/john-penntech/kitchen-rtspx-home-assistant/actions/workflows/test.yml/badge.svg)](https://github.com/john-penntech/kitchen-rtspx-home-assistant/actions/workflows/test.yml)
[![HACS](https://github.com/john-penntech/kitchen-rtspx-home-assistant/actions/workflows/hacs.yml/badge.svg)](https://github.com/john-penntech/kitchen-rtspx-home-assistant/actions/workflows/hacs.yml)
[![Hassfest](https://github.com/john-penntech/kitchen-rtspx-home-assistant/actions/workflows/hassfest.yml/badge.svg)](https://github.com/john-penntech/kitchen-rtspx-home-assistant/actions/workflows/hassfest.yml)

`kitchen_rtspx` hands local `rtspx://` camera sources directly to Home
Assistant's built-in go2rtc stream provider. Version 1.1.0 adds a GUI config
flow, HACS distribution, protected reconfiguration, and redacted diagnostics.

This integration is intended for local streams such as secure UniFi Protect
links. It deliberately rejects non-RTSPX URLs and any `enableSrtp` query option,
which would bypass the intended native go2rtc path.

## Install with HACS

1. Install and configure [HACS](https://www.hacs.xyz/docs/use/download/download/).
2. Open HACS, select the three-dot menu, then **Custom repositories**.
3. Add `https://github.com/john-penntech/kitchen-rtspx-home-assistant` as an
   **Integration** repository.
4. Search for **RTSPX Camera Bridge**, download the latest release, and restart
   Home Assistant.

[![Open your Home Assistant instance and add this repository to HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=john-penntech&repository=kitchen-rtspx-home-assistant&category=integration)

## Add cameras in the GUI

In Home Assistant, open **Settings > Devices & services > Add integration**,
search for **RTSPX Camera Bridge**, and enter:

- **Camera name**: the display name.
- **Camera ID**: a permanent lowercase identifier, such as `patio_camera`.
- **RTSPX stream URL**: the full credential-bearing `rtspx://` source. The field
  is masked, and diagnostics redact it completely.

Repeat the flow for each camera. Use the integration's **Configure** action to
change a camera name or URL later.

## Migrate from the v1.0.0 YAML platform

Version 1.1.0 still understands the original YAML so upgrades are reversible.
For each existing camera, record its `name`, `unique_id`, and secret-backed URL.
Then:

1. Back up `/config`, install v1.1.0, and restart while keeping the YAML.
2. Remove the `platform: kitchen_rtspx` block and run `ha core check`.
3. Restart Home Assistant.
4. Add each camera through the GUI using its old `unique_id` as **Camera ID**.
5. Verify the entity IDs and dashboards before removing the backup.

Reusing the old Camera ID lets Home Assistant's entity registry retain the
existing entity ID. Never paste a stream URL into an issue, log, screenshot, or
Git repository.

## Manual installation

Copy `custom_components/kitchen_rtspx` to Home Assistant's
`/config/custom_components/` directory, run `ha core check`, and restart. HACS
is recommended because it gives users a normal update path.

## Verification and support

```text
python -m compileall -q custom_components tests
python -m unittest discover -s tests -v
```

Repository checks validate the manifest, HACS layout, translations, config
entry and legacy setup paths, URL policy, and absence of high-risk execution or
write primitives. See [ROLLBACK.md](ROLLBACK.md),
[PROVENANCE.md](PROVENANCE.md), and the
[architecture decision](docs/adr/0001-native-go2rtc-rtspx-camera-platform.md).

This is an independent local integration, not an official Home Assistant,
HACS, go2rtc, or Ubiquiti project. Report bugs through
[GitHub Issues](https://github.com/john-penntech/kitchen-rtspx-home-assistant/issues).
