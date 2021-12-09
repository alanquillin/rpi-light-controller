from flask import request

from resources import BaseResource, ResourceMixinBase
from db import session_scope
from db.devices import Devices as DevicesDB


class DeviceResourceMixin(ResourceMixinBase):
    def __init__(self):
        super().__init__()
    
    def transform_response(self, device, **kwargs):
        data = device.to_dict()
        return super().transform_response(data, **kwargs)


class Devices(BaseResource, DeviceResourceMixin):
    def __init__(self):
        super().__init__()

    def get(self):
        with session_scope(self.config) as db_session:
            search = {}
            def _get_search_params(_key):
                _val = request.args.get(_key)
                if _val:
                    search[_key] = _val
            
            for k in ['manufacturer', 'manufacturer_id', 'model']:
                _get_search_params(k)

            if search:
                self.logger.debug("searching for devices with: %s", search)
                devices = DevicesDB.query(db_session, **search)
            else:
                devices = DevicesDB.all(db_session)
            return [self.transform_response(d) for d in devices]

    def post(self):
        with session_scope(self.config) as db_session:
            data = request.get_json()
            data['manufacturer_id'] = data.pop('manufacturerId')
            
            #HACK... not sure why the auto increment is not working in sqlalchemy... works on the DB.. so this is a temp fix
            devices = DevicesDB.all(db_session)
            ids = [d.to_dict()['id'] for d in devices]
            if ids:
                data['id'] = max(ids) + 1
            else: data['id'] = 1
            
            self.logger.debug("Creating device with: %s", data)
            zone = DevicesDB.create(db_session, **data)

            return self.transform_response(zone)

class Device(BaseResource, DeviceResourceMixin):
    def __init__(self):
        super().__init__()

    def get(self, device_id):
        with session_scope(self.config) as db_session:
            zone = DevicesDB.get_by_pkey(db_session, device_id)
            
            return self.transform_response(zone)
    
    def patch(self, device_id):
        with session_scope(self.config) as db_session:
            data = request.get_json()
            
            if data.get("id"):
                data.pop("id")

            if data.get("manufacturerId"):
                data['manufacturer_id'] = data.pop('manufacturerId')

            self.logger.debug("Updating device %s with: %s", device_id, data)
            DevicesDB.update(db_session, device_id, **data)
            device = DevicesDB.get_by_pkey(db_session, device_id)

            return self.transform_response(device)
        
    def delete(self, device_id):
        with session_scope(self.config) as db_session:
            DevicesDB.delete(db_session, device_id)

            return
