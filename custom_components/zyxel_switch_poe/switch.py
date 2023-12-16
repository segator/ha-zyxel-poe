import logging

from homeassistant.core import callback
from homeassistant.const import STATE_ON, STATE_OFF
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import KEY_POESWITCH, DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[KEY_POESWITCH][config_entry.entry_id]

    entities = list()
    for port_idx, _ in coordinator.ports.items():
        entities.append(ZyxelPoeSwitch(coordinator, port_idx))
    _LOGGER.debug(f'Configuring {len(entities)} switches')
    async_add_entities(entities, update_before_add=False)

class ZyxelPoeSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator, port_idx):
        super().__init__(coordinator, context=port_idx)
        self._attr_name = f"{coordinator._name} port{self.coordinator_context}"
        self._attr_is_on = self.coordinator.get_port_state(self.coordinator_context) == STATE_ON
        self._attr_unique_id = f"{self.coordinator._host}_{self.coordinator_context}_poe_switch"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={
                (DOMAIN, self.coordinator._host)
            }
        )

    async def async_turn_on(self):
        _LOGGER.debug(f"Turning on switch {self.coordinator_context}")
        self.coordinator.set_port_state(self.coordinator_context, STATE_ON)
        await self.coordinator.change_state()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self):
        _LOGGER.debug(f"Turning off switch {self.coordinator_context}")
        self.coordinator.set_port_state(self.coordinator_context, STATE_OFF)
        await self.coordinator.change_state()
        await self.coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_on = self.coordinator.get_port_state(self.coordinator_context) == STATE_ON
        _LOGGER.debug(f"State of port {self.coordinator_context} changed to {self._attr_is_on}")
        self.async_write_ha_state()
