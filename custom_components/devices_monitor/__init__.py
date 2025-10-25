from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN
from .devices_monitor import async_setup_runtime

async def async_setup(hass: HomeAssistant, config: dict):
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data.setdefault(DOMAIN, {})
    cfg = {**entry.data, **entry.options}
    hass.data[DOMAIN][entry.entry_id] = cfg
    await async_setup_runtime(hass, entry.entry_id, cfg)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True
