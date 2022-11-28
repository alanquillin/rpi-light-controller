# pylint: disable=wrong-import-position
_TABLE_NAME = "device_zones"
_PKEY = "id"

from sqlalchemy import Column, Integer
from sqlalchemy.orm import backref, relationship
from sqlalchemy.schema import Index, ForeignKey

from db import (
    Base,
    devices,
    zones,
    DictifiableMixin,
    QueryMethodsMixin
)


class DeviceZones(Base, DictifiableMixin, QueryMethodsMixin):

    __tablename__ = _TABLE_NAME

    id = Column(_PKEY, Integer, primary_key=True, autoincrement=True)
    device_id = Column(Integer, ForeignKey("devices.id"), index=True, nullable=False)
    zone_id = Column(Integer, ForeignKey("zones.id"), index=True, nullable=False)
    pin_num = Column(Integer, nullable=False)
    
    device = relationship(devices.Devices,  backref=backref("Devices", cascade="all,delete"))
    zone = relationship(zones.Zones, backref=backref("Zones", cascade="all,delete"))

    __table_args__ = (
        Index("ix_unique_device_id_zone_id_pin", device_id, zone_id, pin_num, unique=True),
    )