from homeassistant.core import HomeAssistant
from homeassistant.util.dt import now
from .const import DOMAIN

async def async_setup_runtime(hass: HomeAssistant, entry_id: str, cfg: dict):
    async def handle_send_report(call):
        target = call.data.get('target','both')
        hass.bus.async_fire('devices_monitor_report', {'target': target})
    hass.services.async_register(DOMAIN,'send_report',handle_send_report)

    async def test_sw(call):
        hass.bus.async_fire('devices_monitor_test_switches',{})
    hass.services.async_register(DOMAIN,'test_switches_notify',test_sw)

    async def test_sn(call):
        hass.bus.async_fire('devices_monitor_test_sensors',{})
    hass.services.async_register(DOMAIN,'test_sensors_notify',test_sn)
