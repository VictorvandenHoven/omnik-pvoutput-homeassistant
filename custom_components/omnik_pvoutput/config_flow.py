from __future__ import annotations

from typing import Any

import voluptuous as vol
from aiohttp import ClientError
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import OmnikPortalApi, validate_omnik_connection
from .const import (
    CONF_INTERVAL,
    CONF_OMNIK_API_URL,
    CONF_OMNIK_INVERTER,
    CONF_OMNIK_INVERTER_ID,
    CONF_OMNIK_PASSWORD,
    CONF_OMNIK_USERNAME,
    CONF_PVOUTPUT_API_KEY,
    CONF_PVOUTPUT_SYSTEM_ID,
    DEFAULT_INTERVAL,
    DEFAULT_OMNIK_API_URL,
    DOMAIN,
)

import logging

_LOGGER = logging.getLogger(__name__)


class OmnikPVOutputConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return OmnikPVOutputOptionsFlow()
    
    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                session = async_get_clientsession(self.hass)
                api = OmnikPortalApi(
                    session,
                    user_input[CONF_OMNIK_API_URL],
                    user_input[CONF_OMNIK_USERNAME],
                    user_input[CONF_OMNIK_PASSWORD],
                    user_input[CONF_OMNIK_INVERTER],
                    int(user_input[CONF_OMNIK_INVERTER_ID]),
                )
                await validate_omnik_connection(api)
            except (ClientError, TimeoutError) as err:
                _LOGGER.exception("Could not connect to OmnikPortal: %s", err)
                errors["base"] = "cannot_connect"

            except RuntimeError as err:
                _LOGGER.exception("OmnikPortal returned an error: %s", err)
                errors["base"] = "invalid_auth"

            except Exception as err:
                _LOGGER.exception(
                    "Unexpected error while validating OmnikPortal connection: %s",
                    err,
                )
                errors["base"] = "unknown"


            if not errors:
                await self.async_set_unique_id(
                    f"{user_input[CONF_OMNIK_INVERTER]}-{user_input[CONF_OMNIK_INVERTER_ID]}"
                )
                self._abort_if_unique_id_configured()
                interval = user_input.pop(CONF_INTERVAL)
                return self.async_create_entry(
                    title=f"Omnik {user_input[CONF_OMNIK_INVERTER]}",
                    data=user_input,
                    options={CONF_INTERVAL: interval},
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_OMNIK_API_URL, default=DEFAULT_OMNIK_API_URL): str,
                vol.Required(CONF_OMNIK_USERNAME): str,
                vol.Required(CONF_OMNIK_PASSWORD): str,
                vol.Required(CONF_OMNIK_INVERTER): str,
                vol.Required(CONF_OMNIK_INVERTER_ID, default=1): vol.Coerce(int),
                vol.Required(CONF_PVOUTPUT_API_KEY): str,
                vol.Required(CONF_PVOUTPUT_SYSTEM_ID): str,
                vol.Required(CONF_INTERVAL, default=DEFAULT_INTERVAL): vol.All(
                    vol.Coerce(int), vol.Range(min=60)
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)


class OmnikPVOutputOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_INTERVAL,
                    default=DEFAULT_INTERVAL,
                ): vol.All(vol.Coerce(int), vol.Range(min=60)),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                schema,
                self.config_entry.options,
            ),
        )

