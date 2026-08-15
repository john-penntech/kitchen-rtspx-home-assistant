# RTSPX Camera Bridge

Install through HACS, restart Home Assistant, then add **RTSPX Camera Bridge**
from **Settings > Devices & services**. Add one config entry per camera.

The stream URL must use `rtspx://`, include a host and stream path, and omit the
`enableSrtp` query option. URLs are masked in the GUI and redacted from
diagnostics.

Legacy `camera: - platform: kitchen_rtspx` definitions are imported as GUI
config entries on the first v1.1.1 restart. Verify the imported entries, remove
the YAML block, run `ha core check`, and restart again.

Full installation, migration, and rollback instructions are maintained in the
[repository README](https://github.com/john-penntech/kitchen-rtspx-home-assistant).
