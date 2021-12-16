import requests
from requests.api import get

from lib.config import Config
from lib import logging

CONFIG = Config()

LOG = logging.getLogger(__name__)

BASE_URL = CONFIG.get("particle.base_url", "https://api.particle.io")

def _req(fn):
    def wrapper(device, path, **kwargs):
        api_key = CONFIG.get("particle.api_key")

        if not api_key:
            LOG.warning("Alerts are enabled for Particle device, but no API key was provided.")
            return

        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        url = f'{BASE_URL}/v1/devices/{device.manufacturer_id}{path}'
        return fn(device, url, headers=headers, **kwargs)
    return wrapper

@_req
def _get(device, uri, **kwargs):
    return requests.get(uri, **kwargs)

@_req
def _post(device, uri, **kwargs):
    return requests.post(uri, **kwargs)

@_req
def _put(device, uri, **kwargs):
    return requests.post(uri, **kwargs)

def _enabled():
    return CONFIG.get("particle.device_services.enabled", False)

def _particle_func(fn):
    def wrapper(*args, **kwargs):
        enabled = _enabled()

        if not enabled:
            LOG.info("Services are not enabled for Particle devices.")
            return

        return fn(*args, **kwargs)
    return wrapper

@_particle_func
def ping(device):
    try:
        data = _put(device, '/ping').json()
        return data.get("online", False)
    except Exception as ex:
        print(ex)
        return False

@_particle_func
def alert(device, *args, **kwargs):
    try:
        resp = _post(device, "/alert")
        LOG.debug("RESPOMNSE: %s", resp)
        return resp.json()
    except Exception as ex:
        LOG.exception("There was an error trying to execute the cloud function for device manufacturer id: %s", device.manufacturer_id)

@_particle_func
def get_details(device, *args, **kwargs):
    try:
        return _get(device, "").json()
    except Exception as ex:
        LOG.exception("There was an error trying to execute the cloud function for device manufacturer id: %s", device.manufacturer_id)

@_particle_func
def get_description(device, *args, **kwargs):
    try:
        details = get_details(device, *args, **kwargs)
        if not details:
            return
        
        return details.get("name")
    except Exception as ex:
        LOG.exception("There was an error trying to execute the cloud function for device manufacturer id: %s", device.manufacturer_id)

def supports_status_check(device, *args, **kwargs):
    return _enabled()