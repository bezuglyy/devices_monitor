import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.selector import (
    EntitySelector, EntitySelectorConfig, TextSelector, NumberSelector
)
from .const import *

def _normalize_ml(value):
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, str):
        parts = []
        for chunk in value.replace("\r", "").split("\n"):
            parts.extend(chunk.split(","))
        return [p.strip() for p in parts if p.strip()]
    return []

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            mode = user_input.get(CONF_MODE, "both")
            # normalize multi-line text fields now
            if CONF_SENSORS_NOTIFY_ALERTS in user_input:
                user_input[CONF_SENSORS_NOTIFY_ALERTS] = _normalize_ml(user_input.get(CONF_SENSORS_NOTIFY_ALERTS, "notify.dom"))
            if CONF_SENSORS_NOTIFY_TTS in user_input:
                user_input[CONF_SENSORS_NOTIFY_TTS] = _normalize_ml(user_input.get(CONF_SENSORS_NOTIFY_TTS, ""))
            return self.async_create_entry(title="Devices Monitor", data=user_input)

        # Base schema
        schema = vol.Schema({
            vol.Required(CONF_MODE, default="both"): vol.In(["switches", "sensors", "both"]),
            vol.Required(CONF_INTERVAL, default=10): NumberSelector({"min":1,"max":120,"unit_of_measurement":"мин","mode":"slider"}),
            vol.Optional(CONF_REPORT_SCHEDULE, default="09:00\n21:00"): TextSelector({"multiline": True}),
        })
        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_options(self, user_input=None):
        return await self.async_step_user(user_input)  # not used

    @staticmethod
    def async_get_options_flow(config_entry):
        return OptionsFlow(config_entry)

class OptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        data = self.config_entry.data
        if user_input is not None:
            user_input[CONF_SENSORS_NOTIFY_ALERTS] = _normalize_ml(user_input.get(CONF_SENSORS_NOTIFY_ALERTS, data.get(CONF_SENSORS_NOTIFY_ALERTS, "notify.dom")))
            user_input[CONF_SENSORS_NOTIFY_TTS] = _normalize_ml(user_input.get(CONF_SENSORS_NOTIFY_TTS, data.get(CONF_SENSORS_NOTIFY_TTS, "")))
            return self.async_create_entry(title="", data=user_input)

        mode = self.config_entry.data.get(CONF_MODE, "both")
        def _get(k, d=None): 
            return self.config_entry.options.get(k, self.config_entry.data.get(k, d))

        # common
        schema = {
            vol.Required(CONF_MODE, default=_get(CONF_MODE, "both")): vol.In(["switches","sensors","both"]),
            vol.Required(CONF_INTERVAL, default=_get(CONF_INTERVAL, 10)): NumberSelector({"min":1,"max":120,"unit_of_measurement":"мин","mode":"slider"}),
            vol.Optional(CONF_REPORT_SCHEDULE, default=_get(CONF_REPORT_SCHEDULE, "09:00\n21:00")): TextSelector({"multiline": True}),
        }

        # switches
        if mode in ["switches","both"]:
            schema.update({
                vol.Optional(CONF_SWITCHES_LIST, default=_get(CONF_SWITCHES_LIST, [])): EntitySelector(EntitySelectorConfig(domain=["switch","light"], multiple=True)),
                vol.Required(CONF_SWITCHES_NOTIFY_ON, default=_get(CONF_SWITCHES_NOTIFY_ON, "notify.dom")): TextSelector({"multiline": False}),
                vol.Required(CONF_SWITCHES_NOTIFY_OFF, default=_get(CONF_SWITCHES_NOTIFY_OFF, "notify.dom")): TextSelector({"multiline": False}),
                vol.Required(CONF_SWITCHES_NOTIFY_REPORT, default=_get(CONF_SWITCHES_NOTIFY_REPORT, "notify.dom")): TextSelector({"multiline": False}),
            })

        # sensors
        if mode in ["sensors","both"]:
            alerts_val = _get(CONF_SENSORS_NOTIFY_ALERTS, "notify.dom")
            alerts_text = "\n".join(alerts_val) if isinstance(alerts_val, list) else str(alerts_val)
            tts_val = _get(CONF_SENSORS_NOTIFY_TTS, [])
            tts_text = "\n".join(tts_val) if isinstance(tts_val, list) else str(tts_val)

            schema.update({
                vol.Optional(CONF_SENSORS_BINARY, default=_get(CONF_SENSORS_BINARY, [])): EntitySelector(EntitySelectorConfig(domain=["binary_sensor"], multiple=True)),
                vol.Optional(CONF_SENSORS_THRESHOLDS, default=_get(CONF_SENSORS_THRESHOLDS, "")): TextSelector({"multiline": True}),
                vol.Required(CONF_SENSORS_NOTIFY_ON, default=_get(CONF_SENSORS_NOTIFY_ON, "notify.dom")): TextSelector({"multiline": False}),
                vol.Required(CONF_SENSORS_NOTIFY_OFF, default=_get(CONF_SENSORS_NOTIFY_OFF, "notify.dom")): TextSelector({"multiline": False}),
                vol.Required(CONF_SENSORS_NOTIFY_ALERTS, default=alerts_text): TextSelector({"multiline": True}),
                vol.Optional(CONF_SENSORS_NOTIFY_TTS, default=tts_text): TextSelector({"multiline": True}),
            })

        return self.async_show_form(step_id="init", data_schema=vol.Schema(schema))
