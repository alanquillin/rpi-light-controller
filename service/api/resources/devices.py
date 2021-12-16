from flask import request

from resources import BaseResource, ResourceMixinBase
from db import session_scope
from db.devices import Devices as DevicesDB
from lib import devices as devicesLib

class DeviceResourceMixin(ResourceMixinBase):
    def __init__(self):
        super().__init__()
    
    def get_status(self, device):
        status = "unsupported"
        if devicesLib.supports_status_check(device):
            status = devicesLib.ping(device)
        return status

    def transform_response(self, device, include_status=False, **kwargs):
        data = device.to_dict()

        data["supports_status_check"] = devicesLib.supports_status_check(device)
        
        include_status = request.args.get("include_status", "false").lower() in ["true", "yes", "", "1"]
        if include_status:
            data["status"] = self.get_status(device)

        include_extended_details = request.args.get("include_extended_details", "false").lower() in ["true", "yes", "", "1"]
        if include_extended_details:
            extended_details = devicesLib.get_details(device)
            if extended_details:
                data["extended_details"] = extended_details

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
            device = DevicesDB.create(db_session, **data)

            if "description" not in data:
                self.logger.debug("no name/description provided... attempting to retrieve int.")
                description = devicesLib.get_description(device)

                if description:
                    self.logger.debug("Yay!  Name/description was able to be retrieved for device %s, updating DB.  value= %s", device.id, description)
                    device = DevicesDB.update(db_session, device.id, description=description)
                else:
                    self.logger.debug(":( unable to retrieve name/descritpion for device %s", device.id)

            return self.transform_response(device)

class Device(BaseResource, DeviceResourceMixin):
    def __init__(self):
        super().__init__()

    def get(self, device_id):
        with session_scope(self.config) as db_session:
            device = DevicesDB.get_by_pkey(db_session, device_id)
            
            return self.transform_response(device)
    
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

class DeviceStatus(BaseResource, ResourceMixinBase):
    def __init__(self):
        super().__init__()

    def get(self, device_id):
        with session_scope(self.config) as db_session:
            device = DevicesDB.get_by_pkey(db_session, device_id)
            
            return self.transform_response(devicesLib.ping(device))

class DeviceExtendedDetails(BaseResource, ResourceMixinBase):
    def __init__(self):
        super().__init__()

    def get(self, device_id):
        with session_scope(self.config) as db_session:
            device = DevicesDB.get_by_pkey(db_session, device_id)
            
            return self.transform_response(devicesLib.get_details(device))
    