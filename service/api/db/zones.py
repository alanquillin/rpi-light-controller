# pylint: disable=wrong-import-position
_TABLE_NAME = "zones"
_PKEY = "id"

from sqlalchemy import Column, String, Integer

from db import (
    Base,
    DictifiableMixin,
    QueryMethodsMixin
)


class Zones(Base, DictifiableMixin, QueryMethodsMixin):

    __tablename__ = _TABLE_NAME

    id = Column(_PKEY, Integer, primary_key=True, autoincrement=True)
    description = Column(String, nullable=False)
    program = Column(String, nullable=False)
    manual_state = Column(String)
    pin_num = Column(Integer)
    on = Column(String, nullable=False)
    off = Column(String, nullable=False)