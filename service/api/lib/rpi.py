import logging


from lib import ThreadSafeSingleton
from lib.config import Config

class RPi(metaclass=ThreadSafeSingleton):

    def __init__(self):
        self.config = Config()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.initialized_pins = []

        if not self.config.get("rpi.simulate"):
            import RPi.GPIO as GPIO

            self.GPIO = GPIO
        else:
            self.GPIO = FakeGPIO()

        mode_str = self.config.get("rpi.mode", "bcm").lower()
        mode = self.GPIO.BOARD
        if mode_str in ["bcm", "gpio"]:
            mode = self.GPIO.BCM

        self.GPIO.setmode(mode)

    def _initialize_zone(self, zone) -> None:
        zone_id = zone.id
        pin_num = zone.pin_num
        if pin_num in self.initialized_pins or self.config.get("rpi.simulate"):
            return
        
        self.logger.debug('Initializing zone %s on pin %s', zone_id, pin_num)
        self.GPIO.setup(pin_num, self.GPIO.OUT)
        self.initialized_pins.append(pin_num)

    def set(self, zone, state):
        self._initialize_zone(zone)

        self.GPIO.output(zone.pin_num, state)


class FakeGPIO(object):
    BOARD = "board mode"
    BCM = "BCM mode"

    def setmode(self, *_, **__):
        pass

    def setup(self, *_, **__):
        pass

    def output(self, *_, **__):
        pass