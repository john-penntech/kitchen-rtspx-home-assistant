# Provenance

## Ownership

- Responsible owner and maintainer: `@john-penntech`
- Source repository: `john-penntech/kitchen-rtspx-home-assistant`
- Component domain: `kitchen_rtspx`
- Captured baseline version: `1.0.0`
- Current repository version: `1.1.1`

## Capture record

On 2026-08-12, the four text files under
`/config/custom_components/kitchen_rtspx/` were exported read-only from the
owner's Home Assistant instance through its authenticated local terminal.
Temporary export artifacts were removed immediately after capture and a
cache-bypassed request confirmed they were no longer served.

The source snapshot contained no camera URL, credential, local IP address,
entity ID, recording, transcript, or other runtime configuration. Actual stream
links remain in Home Assistant `secrets.yaml` and are excluded from this
repository.

## Deployed snapshot hashes

| File | SHA-256 |
| --- | --- |
| `README.md` | `4955f1e12b1b9c98d8bf4f04ae7375d609e6195100e2c1363b6d34ebfaba20ee` |
| `__init__.py` | `efbcc40c5e279aa6c87498c94bb591c38d4409a6b8117653ba9b0844d82b413f` |
| `camera.py` | `b2262444f60c55dc4af1064a35b594203911dc2a6200cca643004e8bb9d4ad74` |
| `manifest.json` | `7d42a214f4ad7630821bc767951ed461d495fcf8405a922d544e0f57562015d7` |

These hashes identify the immutable v1.0.0 capture and remain verifiable from
commit `7a4a733`. `SHA256SUMS` records the current release files.

## Review boundary

The snapshot is 74 Python lines. Static review and the repository test suite
found no shell/subprocess execution, file writes, dynamic code execution, or
direct network implementation. Package signing and the identity of any author
before this capture remain unknown; this repository establishes provenance from
the captured deployment forward rather than reconstructing undocumented past
history. Version 1.1.0 and later changes are attributable to the public Git
history, pull requests, release tags, and pinned validation workflows in this
repository.
