# pylint: disable=wrong-import-position
_TABLE_NAME = "devices"
_PKEY = "id"

from sqlalchemy import Column, String, Integer
from sqlalchemy.schema import Index

from db import (
    Base,
    DictifiableMixin,
    QueryMethodsMixin
)


class Devices(Base, DictifiableMixin, QueryMethodsMixin):

    __tablename__ = _TABLE_NAME

    id = Column(_PKEY, Integer, primary_key=True, autoincrement=True)
    manufacturer_id = Column(String, nullable=False)
    description = Column(String)
    manufacturer = Column(String, nullable=False)
    model = Column(String, nullable=False)
    
    __table_args__ = (
        Index("ix_unique_manufacturer_manufacturer_id_model", manufacturer_id, manufacturer, model, unique=True),
    )