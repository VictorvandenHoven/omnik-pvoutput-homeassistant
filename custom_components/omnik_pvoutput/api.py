from __future__ import annotations

from datetime import datetime
from typing import Any

from aiohttp import ClientSession


class OmnikPortalApi:
    def __init__(self, session: ClientSession, api_url: str, username: str, password: str,
                 inverter: str, inverter_id: int) -> None:
        self._session = session
        self._api_url = api_url
        self._username = username
        self._password = password
        self._inverter = inverter
        self._inverter_id = inverter_id

    async def get_data(self) -> dict[str, Any]:
        today = datetime.now().strftime("%Y-%m-%d")
        payload = {
            "inverter": self._inverter,
            "inverter_id": self._inverter_id,
            "period": today,
        }

        async with self._session.post(
            self._api_url,
            json=payload,
            auth=(self._username, self._password),
            timeout=30,
        ) as response:
            response.raise_for_status()
            data = await response.json()

        if data.get("error") != 0:
            raise RuntimeError(f"OmnikPortal returned error: {data.get('error')}")

        return data


class PVOutputApi:
    def __init__(self, session: ClientSession, api_key: str, system_id: str) -> None:
        self._session = session
        self._api_key = api_key
        self._system_id = system_id

    async def send(self, measurement: dict[str, Any], total_kwh: float) -> str:
        moment = measurement["moment"]
        dt = datetime.strptime(moment, "%Y-%m-%d %H:%M:%S")

        payload = {
            "d": dt.strftime("%Y%m%d"),
            "t": dt.strftime("%H:%M"),
            "v1": round(total_kwh * 1000),
            "v2": int(measurement["watt"]),
            "v5": float(measurement["temperature"]),
        }
        headers = {
            "X-Pvoutput-Apikey": self._api_key,
            "X-Pvoutput-SystemId": self._system_id,
        }

        async with self._session.post(
            "https://pvoutput.org/service/r2/addstatus.jsp",
            headers=headers,
            data=payload,
            timeout=30,
        ) as response:
            response.raise_for_status()
            return (await response.text()).strip()
