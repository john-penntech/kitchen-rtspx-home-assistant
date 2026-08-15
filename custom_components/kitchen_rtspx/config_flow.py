"""Config flow for RTSPX Camera Bridge."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_NAME
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import (
    CONF_STREAM_SOURCE,
    CONF_UNIQUE_ID,
    DOMAIN,
    EnableSrtpNotAllowed,
    InvalidRtspxUrl,
    validate_rtspx_url,
)


def _schema(defaults: dict[str, Any] | None = None, *, include_id: bool = True) -> vol.Schema:
    """Build the user-facing schema, masking the credential-bearing URL."""
    defaults = defaults or {}
    fields: dict[vol.Marker, Any] = {
        vol.Required(CONF_NAME, default=defaults.get(CONF_NAME, "")): cv.string,
    }
    if include_id:
        fields[vol.Required(CONF_UNIQUE_ID, default=defaults.get(CONF_UNIQUE_ID, ""))] = cv.slug
    fields[
        vol.Required(
            CONF_STREAM_SOURCE,
            default=defaults.get(CONF_STREAM_SOURCE, ""),
        )
    ] = TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD))
    return vol.Schema(fields)


def _validate_input(user_input: dict[str, Any]) -> dict[str, Any]:
    """Normalize and validate user input."""
    return {
        **user_input,
        CONF_NAME: user_input[CONF_NAME].strip(),
        CONF_STREAM_SOURCE: validate_rtspx_url(user_input[CONF_STREAM_SOURCE]),
    }


class KitchenRtspxConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle RTSPX Camera Bridge configuration."""

    VERSION = 1

    async def async_step_import(
        self, import_data: dict[str, Any]
    ) -> ConfigFlowResult:
        """Import one legacy YAML camera without exposing its stream URL."""
        data = _validate_input(import_data)
        await self.async_set_unique_id(data[CONF_UNIQUE_ID])
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title=data[CONF_NAME], data=data)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Add one RTSPX camera."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                data = _validate_input(user_input)
            except EnableSrtpNotAllowed:
                errors[CONF_STREAM_SOURCE] = "enable_srtp_not_allowed"
            except InvalidRtspxUrl:
                errors[CONF_STREAM_SOURCE] = "invalid_rtspx_url"
            else:
                await self.async_set_unique_id(data[CONF_UNIQUE_ID])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=data[CONF_NAME], data=data)

        return self.async_show_form(
            step_id="user",
            data_schema=_schema(user_input),
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Update a camera name or protected stream URL."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                updates = _validate_input(
                    {**user_input, CONF_UNIQUE_ID: entry.data[CONF_UNIQUE_ID]}
                )
            except EnableSrtpNotAllowed:
                errors[CONF_STREAM_SOURCE] = "enable_srtp_not_allowed"
            except InvalidRtspxUrl:
                errors[CONF_STREAM_SOURCE] = "invalid_rtspx_url"
            else:
                await self.async_set_unique_id(entry.unique_id)
                self._abort_if_unique_id_mismatch()
                return self.async_update_reload_and_abort(
                    entry,
                    data_updates=updates,
                    title=updates[CONF_NAME],
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=_schema(dict(entry.data) | (user_input or {}), include_id=False),
            errors=errors,
        )
