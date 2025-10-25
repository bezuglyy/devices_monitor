from datetime import timedelta
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.util.dt import now
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

    last_alert_state = {}

    async def _notify(service: str, title: str, message: str):
        await hass.services.async_call("notify", service.split(".")[-1], {"title": title, "message": message}, blocking=False)

    async def _broadcast(services, title: str, message: str):
        if isinstance(services, str): services = [services]
        for srv in services:
            await _notify(srv, title, message)

    async def _speak(players, message: str):
        for p in players:
            await hass.services.async_call("tts", "yandex_station_say", {"entity_id": p, "message": message}, blocking=False)

    @callback
    async def _sensor_changed(event):
        ent = event.data.get("entity_id")
        new = event.data.get("new_state")
        if not new or ent not in sensors_thr:
            return
        rules = sensors_thr.get(ent, {})
        val = _to_float(new.state)
        if val is None:
            return

        above = rules.get("above")
        below = rules.get("below")
        in_alert = False
        if above is not None and val > above:
            msg = rules.get("message_above", f"{ent} выше {above} (текущее {val})")
            await _broadcast(sn_notify_alerts, f"⚠️ Порог: {ent}", msg)
            if sn_notify_tts:
                await _speak(sn_notify_tts, msg)
            in_alert = True
        if below is not None and val < below:
            msg = rules.get("message_below", f"{ent} ниже {below} (текущее {val})")
            await _broadcast(sn_notify_alerts, f"⚠️ Порог: {ent}", msg)
            if sn_notify_tts:
                await _speak(sn_notify_tts, msg)
            in_alert = True

        if in_alert != last_alert_state.get(ent, False):
            if not in_alert:
                await _broadcast(sn_notify_alerts, f"✅ В норме: {ent}", "Показания в допустимых пределах")
                if sn_notify_tts:
                    await _speak(sn_notify_tts, f"{ent} в норме")
            last_alert_state[ent] = in_alert

    async_track_state_change_event(hass, list(sensors_thr.keys()), _sensor_changed)
