from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback

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


class OmnikPVOutputConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return OmnikPVOutputOptionsFlow(config_entry)

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            await self.async_set_unique_id(
                f"{user_input[CONF_OMNIK_INVERTER]}-{user_input[CONF_OMNIK_INVERTER_ID]}"
            )
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=f"Omnik {user_input[CONF_OMNIK_INVERTER]}",
                data=user_input,
            )

        schema = vol.Schema({
            vol.Required(CONF_OMNIK_API_URL, default=DEFAULT_OMNIK_API_URL): str,
            vol.Required(CONF_OMNIK_USERNAME): str,
            vol.Required(CONF_OMNIK_PASSWORD): str,
            vol.Required(CONF_OMNIK_INVERTER): str,
            vol.Required(CONF_OMNIK_INVERTER_ID, default=1): vol.Coerce(int),
            vol.Required(CONF_PVOUTPUT_API_KEY): str,
            vol.Required(CONF_PVOUTPUT_SYSTEM_ID): str,
            vol.Required(CONF_INTERVAL, default=DEFAULT_INTERVAL): vol.All(vol.Coerce(int), vol.Range(min=60)),
        })
        return self.async_show_form(step_id="user", data_schema=schema)


class OmnikPVOutputOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            new_data = {**self.config_entry.data, CONF_INTERVAL: user_input[CONF_INTERVAL]}
            self.hass.config_entries.async_update_entry(self.config_entry, data=new_data)
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_INTERVAL,
                    default=self.config_entry.data.get(CONF_INTERVAL, DEFAULT_INTERVAL),
                ): vol.All(vol.Coerce(int), vol.Range(min=60)),
            }),
        )
