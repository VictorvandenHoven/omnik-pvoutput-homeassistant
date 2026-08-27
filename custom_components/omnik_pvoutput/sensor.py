from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import UnitOfEnergy, UnitOfPower, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import OmnikCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator: OmnikCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            OmnikPowerSensor(coordinator, entry),
            OmnikEnergySensor(coordinator, entry),
            OmnikTemperatureSensor(coordinator, entry),
            OmnikMomentSensor(coordinator, entry),
            PVOutputStatusSensor(coordinator, entry),
            PVOutputErrorSensor(coordinator, entry),
        ]
    )


class BaseOmnikSensor(CoordinatorEntity[OmnikCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: OmnikCoordinator, entry) -> None:
        super().__init__(coordinator)
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "Omnik / PVOutput",
        }


class OmnikPowerSensor(BaseOmnikSensor):
    _attr_name = "Current power"
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:solar-power"

    @property
    def native_value(self):
        return int(self.coordinator.data.measurement["watt"]) if self.coordinator.data else None


class OmnikEnergySensor(BaseOmnikSensor):
    _attr_name = "Today energy"
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_icon = "mdi:solar-power"

    @property
    def native_value(self):
        return self.coordinator.data.total_kwh if self.coordinator.data else None


class OmnikTemperatureSensor(BaseOmnikSensor):
    _attr_name = "Temperature"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:thermometer"

    @property
    def native_value(self):
        return float(self.coordinator.data.measurement["temperature"]) if self.coordinator.data else None


class OmnikMomentSensor(BaseOmnikSensor):
    _attr_name = "Last measurement"
    _attr_icon = "mdi:clock-outline"

    @property
    def native_value(self):
        return (
            self.coordinator.data.measurement["moment"]
            if self.coordinator.data and self.coordinator.data.measurement
            else None
        )


class PVOutputStatusSensor(BaseOmnikSensor):
    _attr_name = "PVOutput response"
    _attr_icon = "mdi:cloud-upload"

    @property
    def native_value(self):
        return self.coordinator.data.last_pvoutput_response if self.coordinator.data else None


class PVOutputErrorSensor(BaseOmnikSensor):
    _attr_name = "PVOutput error"
    _attr_icon = "mdi:alert-circle-outline"

    @property
    def native_value(self):
        return self.coordinator.data.last_error if self.coordinator.data else None
