# ADR 0001: Use a minimal YAML camera platform for native go2rtc RTSPX

- Status: Superseded by ADR 0002 for configuration; native stream decision retained
- Date: 2026-08-12
- Owner: `@john-penntech`

## Context

The local UniFi Protect camera source is a secure RTSP link. The previously
evaluated Generic Camera/FFmpeg path did not preserve the stream behavior needed
by the kitchen dashboard. Home Assistant's built-in go2rtc provider can consume
the source when the scheme is `rtspx://` and Protect's `?enableSrtp` suffix is
omitted.

The integration needs only to describe camera entities and return each
configured stream source. Home Assistant remains responsible for stream
handling, entity lifecycle, authorization, dashboard access, and all broader
orchestration.

## Decision

Maintain a small YAML camera platform named `kitchen_rtspx` that:

- validates `name`, `unique_id`, and `stream_source` for each configured camera;
- advertises Home Assistant's native `STREAM` feature;
- returns the configured source to the native camera/go2rtc provider;
- keeps stream URLs in `secrets.yaml`; and
- does not implement networking, shell execution, file writes, or another
  orchestration/router layer.

## Consequences

The component is easy to review and keeps the data path native to Home
Assistant, but it remains a custom YAML platform and therefore requires testing
against Home Assistant upgrades. Source tests cannot prove live camera decoding.
Before an upgrade or replacement, back up the component/configuration, run
`ha core check`, and verify playback on the real client device.

## Alternatives considered

- Generic Camera/FFmpeg: rejected for this specific secure RTSP/go2rtc stream
  path based on the live integration behavior already observed.
- A custom proxy or stream server: rejected because it would duplicate native
  Home Assistant/go2rtc responsibilities and enlarge the security boundary.
- Embedding the stream URL in source: rejected because the URL is a credential.
