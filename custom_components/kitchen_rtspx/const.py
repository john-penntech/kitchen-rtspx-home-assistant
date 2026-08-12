"""Constants and input validation for RTSPX Camera Bridge."""

from __future__ import annotations

from urllib.parse import parse_qsl, urlsplit

DOMAIN = "kitchen_rtspx"
CONF_STREAM_SOURCE = "stream_source"
CONF_UNIQUE_ID = "unique_id"


class InvalidRtspxUrl(ValueError):
    """Raised when a stream source is not a usable RTSPX URL."""


class EnableSrtpNotAllowed(ValueError):
    """Raised when an RTSPX URL contains the incompatible enableSrtp option."""


def validate_rtspx_url(value: str) -> str:
    """Validate an RTSPX URL without logging or otherwise exposing it."""
    value = value.strip()
    parsed = urlsplit(value)

    if (
        parsed.scheme.lower() != "rtspx"
        or not parsed.hostname
        or parsed.path in {"", "/"}
    ):
        raise InvalidRtspxUrl

    if any(
        key.lower() == "enablesrtp"
        for key, _ in parse_qsl(parsed.query, keep_blank_values=True)
    ):
        raise EnableSrtpNotAllowed

    return value
