# Rollback

Use an attended Home Assistant maintenance window. Do not remove a working
camera path until a backup and replacement path are confirmed.

1. Back up `/config/custom_components/kitchen_rtspx/`, `configuration.yaml`,
   and the relevant `secrets.yaml` entry using Home Assistant's normal backup
   process.
2. Remove or comment only the `platform: kitchen_rtspx` camera block from
   `configuration.yaml`.
3. Run `ha core check`. If validation fails, restore the backed-up configuration
   and stop.
4. Restart Home Assistant only after the configuration check passes.
5. Confirm the affected camera entities are absent or supplied by the intended
   replacement integration, and verify the dashboard does not contain missing
   entities.
6. After successful validation, remove
   `/config/custom_components/kitchen_rtspx/`. Retain the backup until camera
   playback and still images have been observed on the actual client device.

To restore version 1.0.0, copy the four files whose hashes are listed in
`SHA256SUMS` back to `/config/custom_components/kitchen_rtspx/`, restore the
saved YAML block and secret, run `ha core check`, restart, and verify the real
camera stream. Source tests and Home Assistant configuration validation do not
prove decoded camera pixels.
