from flask import request

from resources import BaseResource, ResourceMixinBase
from db import session_scope
from db.zones import Zones as ZonesDB
from lib.rpi import RPi
from lib import zones as zoneLib
from lib.zones import PROGRAM_MANUAL

class ZoneResourceMixin(ResourceMixinBase):
    def __init__(self):
        super().__init__()
        self.gpio = RPi()

    def transform_state(self, state):
        return zoneLib.STATE_ON if state else zoneLib.STATE_OFF
        
    def transform_response(self, zone, **kwargs):
        data = zone.to_dict()
        manual_state = data.pop("manual_state")

        data["state"] = self.transform_state(self.gpio.get(zone))
        
        expected_state = zoneLib.STATE_OFF
        if zone.program == zoneLib.PROGRAM_TIMER:
            expected_state = zoneLib.calc_timer_state(zone)
        elif zone.program == zoneLib.PROGRAM_MANUAL:
            expected_state = manual_state
        
        data["expected_state"] = expected_state

        return super().transform_response(data, **kwargs)

class Zones(BaseResource, ZoneResourceMixin):
    def __init__(self):
        super().__init__()

    def get(self):
        with session_scope(self.config) as db_session:
            zones = ZonesDB.all(db_session)
            return [self.transform_response(z) for z in zones]

    def post(self):
        with session_scope(self.config) as db_session:
            data = request.get_json()
            data['pin_num'] = int(data.pop('pinNum'))
            
            #HACK... not sure why the auto increment is not working in sqlalchemy... works on the DB.. so this is a temp fix
            zones = ZonesDB.all(db_session)
            ids = [z.to_dict()['id'] for z in zones]
            if ids:
                data['id'] = max(ids) + 1
            else: data['id'] = 1
            
            self.logger.debug("Creating zone with: %s", data)
            zone = ZonesDB.create(db_session, **data)

            return self.transform_response(zone)

class Zone(BaseResource, ZoneResourceMixin):
    def __init__(self):
        super().__init__()

    def get(self, zone_id):
        with session_scope(self.config) as db_session:
            zone = ZonesDB.get_by_pkey(db_session, zone_id)
            
            return self.transform_response(zone)
    
    def patch(self, zone_id):
        with session_scope(self.config) as db_session:
            data = request.get_json()
            original_zone = ZonesDB.get_by_pkey(db_session, zone_id)
            
            if data.get("pinNum"):
                data['pin_num'] = int(data.pop('pinNum'))

            if data.get("manualState"):
                data["manual_state"] = data.pop("manualState")
            
            prog_changed_to_manual = False
            if data.get("program") == "manual" and original_zone.program != "manual":
                self.logger.debug("")
                prog_changed_to_manual = True
                data["manual_state"] = "off"

            self.logger.debug("Updating zone %s with: %s", zone_id, data)
            ZonesDB.update(db_session, zone_id, **data)
            zone = ZonesDB.get_by_pkey(db_session, zone_id)

            if data.get("program") == "off" or prog_changed_to_manual:
                self.gpio.set(zone, False)
            
            return self.transform_response(zone)
        
    def delete(self, zone_id):
        with session_scope(self.config) as db_session:
            ZonesDB.delete(db_session, zone_id)

            return

class ZoneState(BaseResource, ZoneResourceMixin):
    def __init__(self):
        super().__init__()
        
    def post(self, zone_id, state):
        with session_scope(self.config) as db_session:
            zone = ZonesDB.get_by_pkey(db_session, zone_id)
            
            self.gpio.set(zone, True if state.lower() == 'on' else False)
            return self.transform_response(zone)