import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.selector import EntitySelector, EntitySelectorConfig, TextSelector, NumberSelector
from .const import *

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Devices Monitor", data=user_input)
        schema = vol.Schema({
            vol.Required(CONF_MODE, default="both"): vol.In(["switches","sensors","both"]),
            vol.Required(CONF_INTERVAL, default=10): NumberSelector({"min":1,"max":120,"unit_of_measurement":"мин","mode":"slider"}),
            vol.Optional(CONF_SWITCHES_REPORT_SCHEDULE, default="09:00\n21:00"): TextSelector({"multiline": True}),
            vol.Optional(CONF_SENSORS_REPORT_SCHEDULE, default="08:00\n20:00"): TextSelector({"multiline": True}),
        })
        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    def async_get_options_flow(config_entry):
        return OptionsFlow(config_entry)

class OptionsFlow(config_entries.OptionsFlow):
    def __init__(self, entry):
        self.entry = entry
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        schema = {
            vol.Optional(CONF_SWITCHES_LIST, default=self.entry.data.get(CONF_SWITCHES_LIST, [])): EntitySelector(EntitySelectorConfig(domain=["switch","light"], multiple=True)),
            vol.Optional(CONF_SENSORS_BINARY, default=self.entry.data.get(CONF_SENSORS_BINARY, [])): EntitySelector(EntitySelectorConfig(domain=["binary_sensor"], multiple=True)),
            vol.Optional(CONF_SENSORS_THRESHOLDS, default=self.entry.data.get(CONF_SENSORS_THRESHOLDS, {})): TextSelector({"multiline": True}),
        }
        return self.async_show_form(step_id="init", data_schema=vol.Schema(schema))
