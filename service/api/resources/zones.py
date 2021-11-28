from flask import request

from resources import BaseResource, ResourceMixinBase
from db import session_scope
from db.zones import Zones as ZonesDB
from lib.rpi import RPi

class Zones(BaseResource, ResourceMixinBase):
    #@login_required(redirect=False, unauthorized_response={"message": "Unauthorized"})
    def get(self):
        with session_scope(self.config) as db_session:
            zones = ZonesDB.all(db_session)
            return [self.transform_response(z.to_dict()) for z in zones]

class Zone(BaseResource, ResourceMixinBase):
    #@login_required(redirect=False, unauthorized_response={"message": "Unauthorized"})
    def get(self, zone_id):
        with session_scope(self.config) as db_session:
            zone = ZonesDB.get_by_pkey(db_session, zone_id)
            
            return self.transform_response(zone.to_dict())
    
    def patch(self, zone_id):
        with session_scope(self.config) as db_session:
            data = request.get_json()
            self.logger.debug("Updating zone %s with: %s", zone_id, data)
            ZonesDB.update(db_session, zone_id, **data)
            zone = ZonesDB.get_by_pkey(db_session, zone_id)

            if data.get("program") == "off":
                self.gpio.set(zone, False)
            
            return self.transform_response(zone.to_dict())

class ZoneState(BaseResource, ResourceMixinBase):
    def __init__(self):
        super().__init__()
        self.gpio = RPi()
        
    def post(self, zone_id, state):
        with session_scope(self.config) as db_session:
            ZonesDB.update(db_session, zone_id, state=state)
            zone = ZonesDB.get_by_pkey(db_session, zone_id)
            
            self.gpio.set(zone, True if state.lower() == 'on' else False)
            return self.transform_response(zone.to_dict())