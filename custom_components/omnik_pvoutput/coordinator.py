from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from aiohttp import ClientError
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import OmnikPortalApi, PVOutputApi
from .const import (
    ATTR_LAST_RESPONSE,
    ATTR_LAST_SENT,
    CONF_INTERVAL,
    CONF_OMNIK_API_URL,
    CONF_OMNIK_INVERTER,
    CONF_OMNIK_INVERTER_ID,
    CONF_OMNIK_PASSWORD,
    CONF_OMNIK_USERNAME,
    CONF_PVOUTPUT_API_KEY,
    CONF_PVOUTPUT_SYSTEM_ID,
    DEFAULT_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class OmnikData:
    measurement: dict[str, Any] | None = None
    total_kwh: float | None = None
    last_sent_moment: str | None = None
    last_pvoutput_response: str | None = None
    last_error: str | None = None


class OmnikCoordinator(DataUpdateCoordinator[OmnikData]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        data = entry.data
        session = async_get_clientsession(hass)

        self.omnik = OmnikPortalApi(
            session,
            data[CONF_OMNIK_API_URL],
            data[CONF_OMNIK_USERNAME],
            data[CONF_OMNIK_PASSWORD],
            data[CONF_OMNIK_INVERTER],
            int(data[CONF_OMNIK_INVERTER_ID]),
        )
        self.pvoutput = PVOutputApi(
            session,
            data[CONF_PVOUTPUT_API_KEY],
            data[CONF_PVOUTPUT_SYSTEM_ID],
        )
        self.last_sent_moment = data.get(ATTR_LAST_SENT)
        self.last_pvoutput_response = data.get(ATTR_LAST_RESPONSE)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=entry,
            update_interval=timedelta(
                seconds=int(entry.options.get(CONF_INTERVAL, DEFAULT_INTERVAL))
            ),
        )

    async def _async_update_data(self) -> OmnikData:
        try:
            data = await self.omnik.get_data()
        except (ClientError, TimeoutError, RuntimeError, ValueError) as err:
            raise UpdateFailed(f"OmnikPortal error: {err}") from err

        data_day = data.get("data_day", [])
        if not data_day:
            raise UpdateFailed("OmnikPortal returned no data_day records")

        try:
            measurement = data_day[-1]
            total_kwh = float(data["data"][0]["watt_total"])
            moment = measurement["moment"]
        except (KeyError, IndexError, TypeError, ValueError) as err:
            raise UpdateFailed(f"Unexpected OmnikPortal response: {err}") from err

        last_error = None
        if moment != self.last_sent_moment:
            try:
                response = await self.pvoutput.send(measurement, total_kwh)
            except (ClientError, TimeoutError, ValueError, KeyError) as err:
                last_error = str(err)
                _LOGGER.error("PVOutput update failed: %s", err)
            else:
                self.last_sent_moment = moment
                self.last_pvoutput_response = response
                self._save_state()
                _LOGGER.info(
                    "PVOutput updated: %s | %s W | %.1f °C | %.2f kWh | %s",
                    moment,
                    int(measurement["watt"]),
                    float(measurement["temperature"]),
                    total_kwh,
                    response,
                )
        else:
            _LOGGER.debug("Measurement %s already sent to PVOutput", moment)

        return OmnikData(
            measurement=measurement,
            total_kwh=total_kwh,
            last_sent_moment=self.last_sent_moment,
            last_pvoutput_response=self.last_pvoutput_response,
            last_error=last_error,
        )

    def _save_state(self) -> None:
        self.hass.config_entries.async_update_entry(
            self.entry,
            data={
                **self.entry.data,
                ATTR_LAST_SENT: self.last_sent_moment,
                ATTR_LAST_RESPONSE: self.last_pvoutput_response,
            },
        )

    async def async_send_now(self) -> bool:
        """Fetch and send the newest measurement when it has not been sent yet."""
        previous = self.last_sent_moment
        await self.async_refresh()
        return self.last_sent_moment != previous
