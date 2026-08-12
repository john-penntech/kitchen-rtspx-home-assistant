# ADR 0002: Distribute through HACS and configure cameras with config entries

- Status: Accepted
- Date: 2026-08-12
- Owner: `@john-penntech`

## Context

The captured v1.0.0 integration required YAML, manual file copies, and direct
secret management. That is reviewable but does not match how a typical HACS user
discovers, installs, updates, or reconfigures an integration.

## Decision

- Publish full semantic GitHub releases in a HACS-compatible repository.
- Create one Home Assistant config entry per camera.
- Require a stable Camera ID so an existing entity registry identity can survive
  YAML-to-GUI migration.
- Mask the credential-bearing stream URL in forms and redact it from diagnostics.
- Validate that sources use `rtspx://`, contain a host and path, and do not set
  `enableSrtp`.
- Retain the v1.0.0 YAML setup path for one compatibility release and document
  backup, migration, and rollback.

## Consequences

Friends can install and update the integration through the same HACS workflow as
other community integrations. Home Assistant owns config-entry lifecycle,
entity registration, stream access, and authorization. The integration still
does not implement transport, proxying, credential exchange, or another intent
router. A Home Assistant backup remains the recovery boundary because config
entry data contains the protected stream URL.
