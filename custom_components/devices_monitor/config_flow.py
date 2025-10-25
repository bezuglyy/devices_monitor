import voluptuous as vol
from homeassistant import config_entries
from .const import *

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Devices Monitor", data=user_input)

        schema = vol.Schema({
            vol.Required(CONF_MODE, default="both"): vol.In(["switches", "sensors", "both"]),
            vol.Required(CONF_INTERVAL, default=10): int,
            vol.Optional(CONF_REPORT_SCHEDULE, default="09:00\n21:00"): str,
        })
        return self.async_show_form(step_id="user", data_schema=schema)
