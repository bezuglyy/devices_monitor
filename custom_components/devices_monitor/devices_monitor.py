from homeassistant.core import HomeAssistant
from .const import *

async def async_setup_runtime(hass: HomeAssistant, entry_id: str, cfg: dict):
    async def handle_test_switches(call):
        await hass.services.async_call("notify", cfg.get(CONF_SWITCHES_NOTIFY_REPORT,"notify.dom").split(".")[-1],
            {"title": "Test Switches", "message": "Тест уведомлений выключателей"})
    hass.services.async_register(DOMAIN, "test_switches_notify", handle_test_switches)

    async def handle_test_sensors(call):
        for srv in cfg.get(CONF_SENSORS_NOTIFY_ALERTS, ["notify.dom"]):
            await hass.services.async_call("notify", srv.split(".")[-1],
                {"title": "Test Sensors", "message": "Тест уведомлений сенсоров"})
    hass.services.async_register(DOMAIN, "test_sensors_notify", handle_test_sensors)

    async def handle_report(call):
        target = call.data.get("target","both")
        await hass.services.async_call("notify", "dom",
            {"title": "Отчёт", "message": f"Формирую отчёт по {target}"})
    hass.services.async_register(DOMAIN, "send_report", handle_report)
