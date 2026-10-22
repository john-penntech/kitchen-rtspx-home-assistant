# HACS update presentation

## What users need to see

Keep release notes focused on the user-visible change, supported Home Assistant
version, steps to apply the update, service interruption, and a support link.
Use a short descriptive release title without repeating the product name and
version: HACS already adds the version above the release body. Include the
integration image in the notes so it is visible even on HACS versions that
cannot resolve local brand assets.

The published v1.1.4 body is maintained in [releases/v1.1.4.md](releases/v1.1.4.md).
Its image URL points to the existing immutable release tag. Editing the GitHub
release title/body changes presentation only; do not move the tag or replace
the existing release assets to correct copy.

## Restart behavior

HACS downloads integration files. Home Assistant must restart to load the new
Python modules. Config-entry reload support does not make Python updates safe
to hot-reload. Do not add a background restart, a second updater, or a monkey
patch to hide the restart requirement.

Explain that users can download several integration updates and restart once,
at a convenient time, after a backup. Include the restart controls, the brief
interruption to Home Assistant services, and moving-video verification. HACS
owns the generic yellow restart warning and its pending-restart state.

## Branding boundary

The supported integration asset is
`custom_components/kitchen_rtspx/brand/icon.png`. It is already included in
v1.1.4 and covered by `SHA256SUMS`. No new image or manifest field is required.

Home Assistant 2026.3 and later serves local integration images through its
authenticated brands API. HACS 2.0.5 instead builds the update entity picture
URL using the central brands CDN, where this custom integration has no icon.
Adding another copy of the same PNG cannot repair that URL. The HACS dashboard
has a related upstream limitation. The inline release image addresses the
release body only, not the update-entity header or every HACS listing.

Upstream closed this issue with the statement that Marketplace in Home
Assistant 2026.11 fixes it. Verify the stable release and rendered icon before
claiming that upgrade resolves it on an installed system. Do not upgrade Home
Assistant merely to change the image.

Sources checked on 2026-10-22:

- [Home Assistant local brands API](https://developers.home-assistant.io/blog/2026/02/24/brands-proxy-api/)
- [HACS 2.0.5 update entity](https://github.com/hacs/integration/blob/2.0.5/custom_components/hacs/update.py)
- [Upstream branding issue and Marketplace resolution](https://github.com/hacs/integration/issues/5402)

## Existing v1.1.4 validation record

The original release reported 11 plugin tests, compilation, release hashes,
`ha core check`, and four minutes of advancing decoded H.264 browser playback.
Physical tablet playback was not independently verified. This copy-only review
does not create new runtime, physical-device, or playback evidence.

The fallback uses the existing managed go2rtc loopback listener for an on-demand
H.264/AAC stream capped at 1280 pixels wide. It preserves the protected RTSPX
source for native WebRTC and reuses the native stream worker. It adds no
external listener or service and redacts fallback errors. The adapter uses
native provider interfaces that still need checking during Home Assistant
upgrades.
