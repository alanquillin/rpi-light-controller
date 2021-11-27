from flask_apispec import use_kwargs
from flask import request
from marshmallow import Schema, fields

from resources import BaseResource, ResourceMixinBase
from db import session_scope
from db.zones import Zones as ZonesDB
from lib.util import is_valid_uuid
from lib.rpi import RPi

#from flask_connect import login_required
class ZoneSchema(Schema):
    id = fields.Int(allow_none=True)
    description = fields.String(allow_none=True)
    program = fields.String(allow_none=True)
    state = fields.String(allow_none=True)
    pin_num = fields.Int(allow_none=True)
    on = fields.String(allow_none=True)
    off = fields.String(allow_none=True)

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
            return self.transform_response(zone.to_dict())

class ZoneState(BaseResource, ResourceMixinBase):
    def __init__(self):
        super().__init__()
        
    def post(self, zone_id, state):
        with session_scope(self.config) as db_session:
            zone = ZonesDB.get_by_pkey(db_session, zone_id)

            ZonesDB.update(db_session, zone.id, state=state)