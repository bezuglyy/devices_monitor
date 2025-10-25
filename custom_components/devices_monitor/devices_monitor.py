from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_state_change_event
from .const import *

def _to_float(val):
    try:
        return float(str(val).replace(",", "."))
    except Exception:
        return None

async def async_setup_runtime(hass: HomeAssistant, entry_id: str, cfg: dict):
    sensors_thr = cfg.get(CONF_SENSORS_THRESHOLDS, {})
    sn_notify_alerts = cfg.get(CONF_SENSORS_NOTIFY_ALERTS, ["notify.dom"])
    sn_notify_tts = cfg.get(CONF_SENSORS_NOTIFY_TTS, [])

    async def _notify(service: str, title: str, message: str):
        await hass.services.async_call("notify", service.split(".")[-1], {"title": title, "message": message}, blocking=False)

    async def _broadcast(services, title: str, message: str):
        if isinstance(services, str): services = [services]
        for srv in services:
            await _notify(srv, title, message)

    async def _speak(players, message: str):
        for p in players:
            await hass.services.async_call("tts", "yandex_station_say", {"entity_id": p, "message": message}, blocking=False)

    # Register test services
    async def handle_test_switches(call):
        await _notify(cfg.get(CONF_SWITCHES_NOTIFY_REPORT, "notify.dom"), "Test Switches", "Тест уведомлений выключателей")
    hass.services.async_register(DOMAIN, "test_switches_notify", handle_test_switches)

    async def handle_test_sensors(call):
        await _broadcast(sn_notify_alerts, "Test Sensors", "Тест уведомлений сенсоров")
        if sn_notify_tts:
            await _speak(sn_notify_tts, "Тест сенсоров")
    hass.services.async_register(DOMAIN, "test_sensors_notify", handle_test_sensors)
