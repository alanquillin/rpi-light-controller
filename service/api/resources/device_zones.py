from flask import request

from db import session_scope
from db.device_zones import DeviceZones as DeviceZonesDB
from resources import BaseResource, ResourceMixinBase
from resources.exceptions import NotFoundError


class DeviceZonesMapResourceMixinBase(ResourceMixinBase):
    def __init__(self):
        super().__init__()

    def transform_response(self, dzs, **kwargs):
        data = [dz.to_dict() for dz in dzs]

        sort_key = kwargs.pop("sort_key")

        map = {}
        for i in data:
            key = i[sort_key]
            pin_num = i["pin_num"]
            if key not in map:
                map[key] = []
            map[key].append(pin_num)
        
        return [ResourceMixinBase.transform_response({sort_key: k, "pin_nums": v}, **kwargs) for k,v in map.items()]

class DeviceZonesResourceMixin(DeviceZonesMapResourceMixinBase):
    def __init__(self):
        super().__init__()

    def transform_response(self, dzs, **kwargs):
        return super().transform_response(dzs, sort_key="zone_id", **kwargs)

class ZoneDevicesResourceMixin(DeviceZonesMapResourceMixinBase):
    def __init__(self):
        super().__init__()

    def transform_response(self, dzs, **kwargs):
        return super().transform_response(dzs, sort_key="device_id", **kwargs)


class DeviceZones(BaseResource, DeviceZonesResourceMixin):
    def __init__(self):
        super().__init__()

    def get(self, device_id):
        with session_scope(self.config) as db_session:
            dzs = DeviceZonesDB.query(db_session, device_id=device_id)
            return self.transform_response(dzs)

    def post(self, device_id):
        with session_scope(self.config) as db_session:
            data = request.get_json()
            data["device_id"] = device_id
            data['zone_id'] = data.pop('zoneId')
            data["pin_num"] = data.pop('pinNum')
            
            #HACK... not sure why the auto increment is not working in sqlalchemy... works on the DB.. so this is a temp fix
            devices = DeviceZonesDB.all(db_session)
            ids = [d.to_dict()['id'] for d in devices]
            if ids:
                data['id'] = max(ids) + 1
            else: data['id'] = 1
            
            self.logger.debug("Mapping zone to device: %s", data)
            dz = DeviceZonesDB.create(db_session, **data)

            return self.transform_response([dz])[0]

class DeviceZone(BaseResource, DeviceZonesResourceMixin):
    def __init__(self):
        super().__init__()

    def get(self, device_id, zone_id):
        with session_scope(self.config) as db_session:
            dzs = DeviceZonesDB.query(db_session, device_id=device_id, zone_id=zone_id)
            
            return self.transform_response(dzs)[0]

class DeviceZonePin(BaseResource):
    def __init__(self):
        super().__init__()

    def delete(self, device_id, zone_id, pin_num):
        with session_scope(self.config) as db_session:
            dz = DeviceZonesDB.query(db_session, device_id=device_id, zone_id=zone_id, pin_num=pin_num)
            if not dz:
                raise NotFoundError()

            DeviceZonesDB.delete(db_session, dz[0].id)

            return

class ZoneDevices(BaseResource, ZoneDevicesResourceMixin):
    def __init__(self):
        super().__init__()

    def get(self, zone_id):
        with session_scope(self.config) as db_session:
            dzs = DeviceZonesDB.query(db_session, zone_id=zone_id)
            return self.transform_response(dzs)

    def post(self, zone_id):
        with session_scope(self.config) as db_session:
            data = request.get_json()
            data["device_id"] = data.pop('deviceId')
            data['zone_id'] = zone_id
            data["pin_num"] = data.pop('pinNum')
            
            #HACK... not sure why the auto increment is not working in sqlalchemy... works on the DB.. so this is a temp fix
            devices = DeviceZonesDB.all(db_session)
            ids = [d.to_dict()['id'] for d in devices]
            if ids:
                data['id'] = max(ids) + 1
            else: data['id'] = 1
            
            self.logger.debug("Mapping zone to device: %s", data)
            dz = DeviceZonesDB.create(db_session, **data)

            return self.transform_response([dz])[0]

class ZoneDevice(BaseResource, ZoneDevicesResourceMixin):
    def __init__(self):
        super().__init__()

    def get(self, device_id, zone_id):
        with session_scope(self.config) as db_session:
            dzs = DeviceZonesDB.query(db_session, device_id=device_id, zone_id=zone_id)
            
            return self.transform_response(dzs)[0]
