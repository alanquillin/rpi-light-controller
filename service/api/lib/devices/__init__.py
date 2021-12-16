from lib.devices import particle
from lib import logging

LOG = logging.getLogger(__name__)

device_functions = {
    "particle": {
        "_default_": {
            "alert": particle.alert,
            "ping": particle.ping,
            "get_details": particle.get_details,
            "get_description": particle.get_description,
            "supports_status_check": particle.supports_status_check
        }
    }
}

def _execute(func_name, device, *args, **kwargs):
    manufacturer = device.manufacturer.lower()
    model = device.model.lower()

    manufacturer_funcs = device_functions.get(manufacturer)
    if not manufacturer_funcs:
        LOG.info("no functions configured for devices with manufacturer: %s", manufacturer)
        return
    
    model_funcs = manufacturer_funcs.get(model)
    if not model_funcs:
        model_funcs = manufacturer_funcs.get("_default_")
    
    if not model_funcs:
        LOG.info("no functions configured for %s devices with model: %s", manufacturer, model)
        return

    fn = model_funcs.get(func_name)
    if not fn:
        LOG.info("no %s function configured for %s devices with model: %s", func_name, manufacturer, model)
        return

    return fn(device, *args, **kwargs)

def alert(device, *args, **kwargs):
    return _execute("alert", device, *args, **kwargs)

def ping(device, *args, **kwargs):
    return _execute("ping", device, *args, **kwargs)

def get_details(device, *args, **kwargs):
    return _execute("get_details", device, *args, **kwargs)

def get_description(device, *args, **kwargs):
    return _execute("get_description", device, *args, **kwargs)

def supports_status_check(device, *args, **kwargs):
    # There is a chance the implementation return None or other falsey values, so explicitely check for True
    return True if _execute("supports_status_check", device, *args, **kwargs) == True else False
