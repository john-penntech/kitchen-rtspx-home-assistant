# Rollback and recovery

## Before changing a Home Assistant installation

Create a Home Assistant backup or copy these items to a protected local backup:

- `/config/custom_components/kitchen_rtspx/`
- the `camera: - platform: kitchen_rtspx` YAML block, if present
- the related `secrets.yaml` keys (never copy their values into this repository)
- `.storage/core.config_entries` and `.storage/core.entity_registry`

Run `ha core check` before every restart.

## Roll back a HACS upgrade

Open HACS, select **RTSPX Camera Bridge**, choose **Redownload**, and select the
previous release. Restart Home Assistant and verify the camera entity states.

## Return to the v1.0.0 YAML platform

1. Remove or disable the GUI config entries.
2. Restore the v1.0.0 `custom_components/kitchen_rtspx/` directory.
3. Restore the original YAML block and secret keys.
4. Run `ha core check`; only restart if it succeeds.
5. Verify the original camera entity IDs and dashboard references.

Do not restore `.storage` files into a running Home Assistant process. If entity
registry recovery is required, stop Home Assistant first or restore the complete
Home Assistant backup through the supported backup UI.
