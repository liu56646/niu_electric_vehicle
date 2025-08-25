"""
Config flow for Niu Electric Vehicle integration.
"""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .const import CONF_VEHICLE_ID, DOMAIN
from .niu_api import NiuApiClient

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_VEHICLE_ID): str,
    }
)

class NiuElectricVehicleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Niu Electric Vehicle."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate credentials
            session = async_create_clientsession(self.hass)
            client = NiuApiClient(
                user_input[CONF_USERNAME],
                user_input[CONF_PASSWORD],
                user_input[CONF_VEHICLE_ID],
                session,
            )

            try:
                # Test connection
                await client.async_authenticate()
                await client.async_get_vehicle_data()
            except Exception as exception:
                _LOGGER.error("Error connecting to Niu API: %s", exception)
                errors["base"] = "cannot_connect"
            else:
                # Create entry
                await self.async_set_unique_id(user_input[CONF_VEHICLE_ID])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Niu Vehicle {user_input[CONF_VEHICLE_ID]}",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_reauth(self, entry_data: dict[str, Any]) -> FlowResult:
        """Handle reauthorization."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm reauthorization."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Update entry with new credentials
            entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
            assert entry is not None

            new_data = entry.data.copy()
            new_data[CONF_USERNAME] = user_input[CONF_USERNAME]
            new_data[CONF_PASSWORD] = user_input[CONF_PASSWORD]

            # Test new credentials
            session = async_create_clientsession(self.hass)
            client = NiuApiClient(
                new_data[CONF_USERNAME],
                new_data[CONF_PASSWORD],
                new_data[CONF_VEHICLE_ID],
                session,
            )

            try:
                await client.async_authenticate()
                await client.async_get_vehicle_data()
            except Exception as exception:
                _LOGGER.error("Error reauthenticating with Niu API: %s", exception)
                errors["base"] = "cannot_connect"
            else:
                # Update entry
                self.hass.config_entries.async_update_entry(entry, data=new_data)
                await self.hass.config_entries.async_reload(entry.entry_id)
                return self.async_abort(reason="reauth_successful")

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )