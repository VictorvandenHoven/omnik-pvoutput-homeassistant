# Omnik Portal PVOutput for Home Assistant

Home Assistant custom integration that polls the OmnikPortal API and forwards the newest inverter measurement to PVOutput.

## Features

- Poll OmnikPortal every 5 minutes by default
- Current power, today's energy and inverter temperature sensors
- Forwards v1 (energy), v2 (power) and v5 (temperature) to PVOutput
- Prevents sending the same measurement twice
- Stores the last sent measurement in the Home Assistant config entry
- Configurable through the Home Assistant UI

## Installation

### HACS

1. Open HACS.
2. Go to **Integrations**.
3. Select **Custom repositories** from the three-dot menu.
4. Add:

   `https://github.com/VictorvandenHoven/omnik-pvoutput-homeassistant`

5. Select **Integration** as the category.
6. Click **Add**.
7. Search for **Omnik Portal PVOutput**.
8. Click **Download**.
9. Restart Home Assistant.
10. Go to **Settings → Devices & services → Add integration**.
11. Search for **Omnik Portal PVOutput**.
