from datetime import timedelta
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_interval, async_track_time_change, async_track_state_change_event
from homeassistant.util.dt import now
from .const import *

def _to_float(val):
    try:
        return float(str(val).replace(",", "."))
    except Exception:
        return None

def _as_list(value):
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, str):
        parts = []
        for chunk in value.replace("\r", "").split("\n"):
            parts.extend(chunk.split(","))
        return [p.strip() for p in parts if p.strip()]
    return []

def _parse_schedule(value):
    items = value if isinstance(value, list) else str(value).splitlines()
    times = []
    for line in items:
        line = line.strip()
        if not line:
            continue
        try:
            hh, mm = [int(x) for x in line.split(":")]
            times.append((hh, mm))
        except Exception:
            continue
    return times

def _parse_thresholds(text):
    rules = []
    if not text:
        return rules
    lines = text if isinstance(text, list) else str(text).splitlines()
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split(";")]
        if not parts:
            continue
        entity_id = parts[0]
        rule = {"entity_id": entity_id}
        for p in parts[1:]:
            if "=" in p:
                k, v = p.split("=", 1)
                k = k.strip().lower()
                v = v.strip()
                if k in ("above","below"):
                    try:
                        rule[k] = float(v.replace(",", "."))
                    except Exception:
                        pass
                elif k == "message":
                    rule[k] = v
        rules.append(rule)
    return rules

async def async_setup_runtime(hass: HomeAssistant, entry_id: str, cfg: dict):
    mode = cfg.get(CONF_MODE, "both")

    # switches
    switches = _as_list(cfg.get(CONF_SWITCHES_LIST, []))
    sw_notify_on = cfg.get(CONF_SWITCHES_NOTIFY_ON, "notify.dom")
    sw_notify_off = cfg.get(CONF_SWITCHES_NOTIFY_OFF, "notify.dom")
    sw_notify_report = cfg.get(CONF_SWITCHES_NOTIFY_REPORT, "notify.dom")
    sw_schedule = _parse_schedule(cfg.get(CONF_SWITCHES_REPORT_SCHEDULE, ""))

    # sensors
    sensors_bin = _as_list(cfg.get(CONF_SENSORS_BINARY, []))
    sensors_thr = _parse_thresholds(cfg.get(CONF_SENSORS_THRESHOLDS, ""))
    sn_notify_on = cfg.get(CONF_SENSORS_NOTIFY_ON, "notify.dom")
    sn_notify_off = cfg.get(CONF_SENSORS_NOTIFY_OFF, "notify.dom")
    sn_notify_alerts = _as_list(cfg.get(CONF_SENSORS_NOTIFY_ALERTS, "notify.dom"))
    sn_notify_tts = _as_list(cfg.get(CONF_SENSORS_NOTIFY_TTS, ""))
    sn_schedule = _parse_schedule(cfg.get(CONF_SENSORS_REPORT_SCHEDULE, ""))

    # common
    interval = int(cfg.get(CONF_INTERVAL, 10))
    last_alert_state = {}  # threshold memory

    async def _notify(service: str, title: str, message: str):
        if not service:
            return
        await hass.services.async_call(
            "notify",
            service.split(".")[1] if "." in service else service,
            {"title": title, "message": message},
            blocking=False
        )

    async def _broadcast(services, title: str, message: str):
        for srv in services:
            await _notify(srv, title, message)

    async def _speak(players, message: str):
        for p in players:
            await hass.services.async_call("tts", "yandex_station_say", {"entity_id": p, "message": message}, blocking=False)

    # ----------------- SWITCHES -----------------
    async def _switch_report_lines():
        lines = []
        for ent in switches:
            st = hass.states.get(ent)
            if st and st.state == "on":
                delta = (now().timestamp() - st.last_changed.timestamp())
                h = int(delta // 3600); m = int((delta % 3600) // 60); s = int(delta % 60)
                name = st.name or ent
                lines.append(f"• {name} (работает уже {h}ч {m}м {s}с)")
        return lines

    @callback
    async def _switch_changed(event):
        ent = event.data.get("entity_id")
        new = event.data.get("new_state")
        old = event.data.get("old_state")
        if not new or not old or ent not in switches:
            return
        name = new.name or ent
        if new.state == "on" and old.state != "on":
            await _notify(sw_notify_on, f"🔌 Включён: {name}", f"✅ Включился в {now().strftime('%H:%M:%S')}")
        elif new.state == "off" and old.state != "off":
            dur = int(now().timestamp() - old.last_changed.timestamp())
            h = dur//3600; m=(dur%3600)//60; s=dur%60
            await _notify(sw_notify_off, f"🔌 Выключён: {name}", f"✅ Работал: {h:02d}:{m:02d}:{s:02d}")

    if mode in ["switches","both"] and switches:
        async_track_state_change_event(hass, switches, _switch_changed)

    # ----------------- SENSORS -----------------
    def _check_threshold(state, rule):
        val = _to_float(state.state) if state else None
        if val is None:
            return False
        above = rule.get("above")
        below = rule.get("below")
        ok = True
        if above is not None and not (val > above):
            ok = False
        if below is not None and not (val < below):
            ok = False
        return ok

    def _format_msg(rule, val):
        msg = rule.get("message") or f"{rule['entity_id']} = {val}"
        return msg.replace("{value}", f"{val}")

    async def _sensors_report_lines():
        lines = []
        # active binary
        for ent in sensors_bin:
            st = hass.states.get(ent)
            if st and st.state == "on":
                delta = (now().timestamp() - st.last_changed.timestamp())
                h = int(delta // 3600); m = int((delta % 3600) // 60); s = int(delta % 60)
                name = st.name or ent
                lines.append(f"• {name} (активно {h}ч {m}м {s}с)")
        # thresholds
        for r in sensors_thr:
            ent = r["entity_id"]
            st = hass.states.get(ent)
            if st and _check_threshold(st, r):
                val = _to_float(st.state)
                lines.append(f"• {ent}: {_format_msg(r, val)}")
        return lines

    @callback
    async def _binary_changed(event):
        ent = event.data.get("entity_id")
        new = event.data.get("new_state")
        old = event.data.get("old_state")
        if not new or not old or ent not in sensors_bin:
            return
        name = new.name or ent
        if new.state == "on" and old.state != "on":
            await _notify(sn_notify_on, f"🚨 Тревога: {name}", "Датчик перешёл в ON")
            if sn_notify_tts:
                await _speak(sn_notify_tts, f"{name} тревога")
        elif new.state == "off" and old.state != "off":
            await _notify(sn_notify_off, f"✅ Норма: {name}", "Датчик перешёл в OFF")
            if sn_notify_tts:
                await _speak(sn_notify_tts, f"{name} в норме")

    thr_entities = [r["entity_id"] for r in sensors_thr if "entity_id" in r]

    @callback
    async def _thr_changed(event):
        ent = event.data.get("entity_id")
        new = event.data.get("new_state")
        if not new or ent not in thr_entities:
            return
        rules = [r for r in sensors_thr if r.get("entity_id") == ent]
        in_alert = any(_check_threshold(new, r) for r in rules)
        was_alert = last_alert_state.get(ent, False)
        if in_alert and not was_alert:
            for r in rules:
                if _check_threshold(new, r):
                    val = _to_float(new.state)
                    msg = _format_msg(r, val)
                    await _broadcast(sn_notify_alerts, f"⚠️ Порог: {ent}", msg)
                    if sn_notify_tts:
                        await _speak(sn_notify_tts, msg)
            last_alert_state[ent] = True
        elif (not in_alert) and was_alert:
            await _broadcast(sn_notify_alerts, f"✅ В норме: {ent}", "Показания в допустимых пределах")
            if sn_notify_tts:
                await _speak(sn_notify_tts, f"{ent} в норме")
            last_alert_state[ent] = False

    if mode in ["sensors","both"]:
        if sensors_bin:
            async_track_state_change_event(hass, sensors_bin, _binary_changed)
        if thr_entities:
            async_track_state_change_event(hass, thr_entities, _thr_changed)

    # ----------------- REPORTING -----------------
    async def _report_switches(_now):
        if not (mode in ["switches","both"] and switches):
            return
        lines = await _switch_report_lines()
        if lines and sw_notify_report:
            await _notify(sw_notify_report, "📈 Отчёт по выключателям", "\n".join(lines))

    async def _report_sensors(_now):
        if not (mode in ["sensors","both"]):
            return
        lines = await _sensors_report_lines()
        if lines:
            if sn_notify_alerts:
                await _broadcast(sn_notify_alerts, "📊 Отчёт по сенсорам", "\n".join(lines))
            if sn_notify_tts:
                await _speak(sn_notify_tts, f"Активных событий: {len(lines)}")

    # interval reports: общий интервал вызывает оба отчёта
    if interval > 0:
        async_track_time_interval(hass, _report_switches, timedelta(minutes=interval))
        async_track_time_interval(hass, _report_sensors, timedelta(minutes=interval))

    # schedule reports
    for hh, mm in sw_schedule:
        async_track_time_change(hass, _report_switches, hour=hh, minute=mm)
    for hh, mm in sn_schedule:
        async_track_time_change(hass, _report_sensors, hour=hh, minute=mm)

    # ----------------- SERVICES -----------------
    async def handle_send_report(call):
        target = call.data.get("target", "both")
        if target in ("switches","both"):
            await _report_switches(now())
        if target in ("sensors","both"):
            await _report_sensors(now())
    hass.services.async_register(DOMAIN, "send_report", handle_send_report)

    async def handle_test_switches(call):
        await _notify(sw_notify_report, "Test Switches", "Тест уведомлений выключателей")
    hass.services.async_register(DOMAIN, "test_switches_notify", handle_test_switches)

    async def handle_test_sensors(call):
        await _broadcast(sn_notify_alerts, "Test Sensors", "Тест уведомлений сенсоров")
        if sn_notify_tts:
            await _speak(sn_notify_tts, "Тест сенсоров")
    hass.services.async_register(DOMAIN, "test_sensors_notify", handle_test_sensors)
