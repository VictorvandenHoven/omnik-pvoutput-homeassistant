# Omnik Portal PVOutput for Home Assistant

Home Assistant custom integration that polls the OmnikPortal API and forwards the newest inverter measurement to PVOutput.

## Features

- Poll OmnikPortal every 5 minutes by default
- Current power, today's energy and inverter temperature sensors
- Forwards v1 (energy), v2 (power) and v5 (temperature) to PVOutput
- Prevents sending the same measurement twice
- Stores the last sent measurement in the Home Assistant config entry
- Configurable through the Home Assistant UI

## HACS

Add this GitHub repository to HACS as a custom repository with category `Integration`, then install `Omnik Portal PVOutput`.

After installation, restart Home Assistant and go to Settings → Devices & services → Add integration.
