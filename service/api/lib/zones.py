import time

from db import session_scope
from db.zones import Zones as ZonesDB
from lib.config import Config
from lib.rpi import RPi

DB_DATE_FORMAT = '%H:%M:%S'

PROGRAM_TIMER = "timer"
PROGRAM_MANUAL = "manual"
PROGRAM_OFF = "off"

STATE_ON = "on"
STATE_OFF = "off"

CONFIG = Config()


def get_time(t):
    now = time.localtime()
    dt = '%s/%s/%s %s' % (now.tm_mon, now.tm_mday, now.tm_year, t)
    format = '%m/%d/%Y {}'.format(DB_DATE_FORMAT)
    return time.strptime(dt, format)

def calc_timer_state(zone):
    if zone.program != PROGRAM_TIMER:
        return None

    now = time.localtime()
    start = get_time(zone.on)
    end = get_time(zone.off)
    
    turn_on = start < now < end
    if start > end:
        turn_on = now < end or now > start

    return turn_on

def initialize():
    rpi = RPi()

    with session_scope(CONFIG) as db_session:
        zones = ZonesDB.all(db_session)

        for zone in zones:
            rpi._initialize_zone(zone)
            if zone.program == PROGRAM_TIMER:
                if calc_timer_state(zone):
                    rpi.set(zone, True)
            if zone.program == PROGRAM_MANUAL:
                if zone.manual_state == STATE_ON:
                    rpi.set(zone, True)