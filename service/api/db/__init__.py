import re
from contextlib import contextmanager
from functools import wraps
from urllib.parse import quote

from psycopg2.errors import (  # pylint: disable=no-name-in-module
    InvalidTextRepresentation,
    NotNullViolation,
    UniqueViolation,
)
from sqlalchemy import create_engine, func, text
from sqlalchemy.exc import DataError, IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.properties import ColumnProperty

from lib import exceptions as local_exc
from lib import json

Base = declarative_base()

__all__ = [
    "zones"
]

@contextmanager
def convert_exception(sqla, psycopg2=None, new=None, param_names=None, str_match=""):
    if param_names is None:
        param_names = []
    try:
        yield
    except sqla as exc:
        if str_match not in str(exc):
            raise

        if param_names:
            args = [str(exc.params.get(param)) for param in param_names]
        else:
            args = [str(exc)]

        if psycopg2 is None:
            raise new() from exc

        if isinstance(exc.orig, psycopg2):
            if not param_names:
                args = [str(exc.orig)]
            raise new(*args) from exc

        raise


def create_session(config, **kwargs):
    engine_kwargs = {
        "connect_args": {"application_name": config.get("app_id", f"UNKNOWN=>({__name__})")},
        "json_serializer": json.dumps,
    }

    password = config.get("db.password")

    engine = create_engine(
        (
            "postgresql://"
            f"{quote(config.get('db.username'))}:{quote(password)}@{quote(config.get('db.host'))}:"
            f"{config.get('db.port')}/{quote(config.get('db.name'))}"
        ),
        **engine_kwargs,
    )

    return sessionmaker(bind=engine, **kwargs)()


@contextmanager
def session_scope(config, **kwargs):
    session = create_session(config, **kwargs)
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def _get_column_value(instance, col_name):
    try:
        return getattr(instance, col_name)
    except AttributeError:
        for attr, column in inspect(instance.__class__).c.items():
            if column.name == col_name:
                return getattr(instance, attr)
    raise AttributeError


class DictifiableMixin:
    def to_dict(self, include_relationships=None):
        result = {}

        for name, attr in inspect(self.__class__).all_orm_descriptors.items():
            if name.startswith("_"):
                continue
            if hasattr(attr, "property") and not isinstance(attr.property, ColumnProperty):
                continue

            name = getattr(attr, "name", name)
            result[name] = _get_column_value(self, name)

        if not include_relationships:
            include_relationships = []

        for rel in include_relationships:
            val = getattr(self, rel)
            if val is not None:
                result[rel] = getattr(self, rel).to_dict()

        return result

    def _json_repr_(self, *args, **kwargs):
        return self.to_dict(*args, **kwargs)


_MERGEABLE_FIELDS_LIST = "_mergeable_fields"


def mergeable_fields(*fields_list):
    def decorator(cls):
        setattr(cls, _MERGEABLE_FIELDS_LIST, fields_list)
        return cls

    return decorator


_ENUM_EXC_MAP = "_custom_exception_map"


def _merge_into(target, updates):
    if target is None:
        return updates

    for k, v in updates.items():
        if k in target and isinstance(v, dict) and isinstance(target[k], dict):
            _merge_into(target[k], v)
        elif k in target and isinstance(v, list) and isinstance(target[k], list):
            target[k].extend(v)
        else:
            target[k] = v
    return target


class QueryMethodsMixin:
    @classmethod
    def query(cls, session, q=None, slice_start=None, slice_end=None, **kwargs):
        if q is None:
            q = session.query(cls).filter_by(**kwargs)

        if not None in [slice_start, slice_end]:
            q = q.slice(slice_start, slice_end)

        try:
            return q.all()
        except DataError as err:
            if not isinstance(err.orig, InvalidTextRepresentation):
                raise
            if "invalid input value for enum" not in str(err.orig):
                raise

            # somewhat finicky parsing of the PG error here
            # expected format returned by str(err.orig):
            # E       psycopg2.errors.InvalidTextRepresentation: invalid input value for enum "OrderType": "invalid"
            # E       LINE 3: ...3-4b88-a6b0-5a01d901233f' AND orders.order_type = 'invalid' ...
            # E                                                                    ^

            msg, desc, pointer, _ = str(err.orig).split("\n")

            # get Enum name from the first line
            enum_name = msg.split("for enum ")[1].split(":")[0].strip('"')
            exc = getattr(cls, _ENUM_EXC_MAP).get(enum_name, local_exc.InvalidEnum)

            # Use the indicator on the third line to find the column name in the second line
            err_ix = pointer.index("^")
            _, column_name = desc[:err_ix].split()[-2].split(".")

            raise exc(err.params.get(column_name, "could not find offending value")) from err

    @classmethod
    def get_by_pkey(cls, session, pkey):
        return session.query(cls).get(pkey)

    @classmethod
    def create(cls, session, autocommit=True, **kwargs):
        for key in kwargs:
            if not hasattr(cls, key):
                raise local_exc.InvalidParameter(key)

        row = cls(**kwargs)
        session.add(row)

        if autocommit:
            try:
                with convert_exception(
                    IntegrityError, psycopg2=NotNullViolation, new=local_exc.RequiredParameterNotFound
                ), convert_exception(
                    IntegrityError, psycopg2=UniqueViolation, new=local_exc.ItemAlreadyExists, str_match="_pkey"
                ):
                    session.commit()
            except:
                session.rollback()
                raise

        return row

    @classmethod
    def update_query(cls, session, filters=None, **updates):
        if filters is None:
            filters = {}

        session.query(cls).filter_by(**filters).update(updates)

    @classmethod
    def update(cls, session, pkey, merge_nested=False, autocommit=True, **kwargs):
        merge_fields = getattr(cls, _MERGEABLE_FIELDS_LIST, [])
        row = cls.get_by_pkey(session, pkey)

        for key, value in kwargs.items():
            if not hasattr(cls, key):
                raise local_exc.InvalidParameter(key)

            if merge_nested and key in merge_fields:
                current = getattr(row, key, {})
                value = _merge_into(current, value)

            setattr(row, key, value)

        session.add(row)
        if autocommit:
            try:
                session.commit()
            except:
                session.rollback()
                raise

        return row

    @classmethod
    def delete(cls, session, pkey, autocommit=True):
        session.delete(cls.get_by_pkey(session, pkey))

        if autocommit:
            try:
                session.commit()
            except:
                session.rollback()
                raise

    @classmethod
    def all(cls, session):
        return session.query(cls).all()