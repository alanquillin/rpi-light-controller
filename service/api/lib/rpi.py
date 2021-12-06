import logging


from lib import ThreadSafeSingleton
from lib.config import Config

class RPi(metaclass=ThreadSafeSingleton):

    def __init__(self):
        self.config = Config()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.initialized_pins = []
        self.state = {}

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
        if not zone.pin_num:
            self.logger.debug("There is no pin number set for zone %s,  skipping initialization.", zone.id)
            return
        
        if zone.pin_num in self.initialized_pins or self.config.get("rpi.simulate"):
            return
        
        if zone.pin_num not in self.state.keys():
            self.state[zone.pin_num] = False

        self.logger.debug('Initializing zone %s on pin %s', zone.id, zone.pin_num)
        self.GPIO.setup(zone.pin_num, self.GPIO.OUT)
        self.initialized_pins.append(zone.pin_num)

    def set(self, zone, state):
        if not zone.pin_num:
            self.logger.debug("There is no pin number set for zone %s,  skipping set.", zone.id)
            return
        self._initialize_zone(zone)
        self.state[zone.pin_num] = state
        self.GPIO.output(zone.pin_num, state)

    def get(self, zone):
        if not zone.pin_num or zone.pin_num not in self.state.keys():
            return False

        return self.state[zone.pin_num]


class FakeGPIO(object):
    BOARD = "board mode"
    BCM = "BCM mode"

    def setmode(self, *_, **__):
        pass

    def setup(self, *_, **__):
        pass

    def output(self, *_, **__):
        pass