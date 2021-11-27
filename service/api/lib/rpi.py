import logging


from lib import ThreadSafeSingleton
from lib.config import Config

class RPi(metaclass=ThreadSafeSingleton):

    def __init__(self):
        self.config = Config()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.initialized_zones = []

        if not self.config.get("rpi.simulate"):
            import RPi.GPIO as GPIO

            self.GPIO = GPIO
        else:
            self.GPIO = FakeGPIO()

        self.GPIO.setmode(self.GPIO.BOARD)

    def _initialize_zone(self, zone) -> None:
        zone_id = zone.id
        if zone_id in self.initialized_zones or self.config.get("rpi.simulate"):
            return
        
        pin_num = zone.pin_num
        self.logger.debug('Initializing zone %s on pin %s', zone_id, pin_num)
        self.GPIO.setup(pin_num, self.GPIO.OUT)
        self.initialized_zones.push(zone_id)

    def set(self, zone, state):
        self._initialize_zone(zone)

        self.GPIO.output(zone.pin_num, state)


class FakeGPIO(object):
    def setmode(self, *_, **__):
        pass

    def setup(self, *_, **__):
        pass

    def output(self, *_, **__):
        pass