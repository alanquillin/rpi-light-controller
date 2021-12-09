#!/usr/bin/env python3

import argparse
import logging
import os
from datetime import datetime, timedelta
from time import sleep
from uuid import uuid4

from lib.util import random_string
from lib.config import Config
from db import (
    Base,
    devices,
    device_zones,
    session_scope,
    zones
)
from sqlalchemy.exc import OperationalError, IntegrityError

ZONES = [
    {
        "id": 1,
        "description": "Zone 1",
        "program": "timer",
        "pin_num": 11,
        "on": "17:00:00",
        "off": "23:59:59"
    },{
        "id": 2,
        "description": "Zone 2",
        "program": "Manual",
        "manual_state": "om",
        "pin_num": 12,
        "on": "17:00:00",
        "off": "23:59:59"
    }
]

DEVICES = [
    {
        "id": 1,
        "description": "Device 1",
        "manufacturer_id": "abc123",
        "manufacturer": "particle",
        "model": "photon"
    },
    {
        "id": 2,
        "description": "Device 2",
        "manufacturer_id": "abc456",
        "manufacturer": "particle",
        "model": "photon"
    }
]

DEVICE_ZONES = [
    {
        "id": 1,
        "device_id": 1,
        "zone_id": 1,
        "pin_num": 1
    },
    {
        "id": 2,
        "device_id": 1,
        "zone_id": 1,
        "pin_num": 2
    },
    {
        "id": 3,
        "device_id": 1,
        "zone_id": 2,
        "pin_num": 3
    },
    {
        "id": 4,
        "device_id": 2,
        "zone_id": 1,
        "pin_num": 4
    }
]

def seed_db(db_session, db, items, pk="id"):
    for item in items:
        logger.info(item)
        try:
            if not db.get_by_pkey(db_session, item[pk]):
                logger.info("Seeding %s: %s", db.__name__, item)
                db.create(db_session, **item)
            else:
                logger.info("Item %s already exists in %s.", item[pk], db.__name__)
        except IntegrityError as ex:
                logger.debug("Item already exists or a constraint was violated: %s", ex.detail)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # parse logging level arg:
    parser.add_argument(
        "-l",
        "--log",
        dest="loglevel",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=os.environ.get("LOG_LEVEL", "INFO").upper(),
        help="Set the logging level",
    )

    args = parser.parse_args()
    log_level = getattr(logging, args.loglevel)
    logging.basicConfig(level=log_level, format="%(levelname)-8s: %(asctime)-15s [%(name)s]: %(message)s")
    logger = logging.getLogger()

    config = Config()
    config.setup()

    logger.debug("config: %s", config.data_flat)
    logger.debug("db host: %s", config.get("db.host"))
    logger.debug("db username: %s", config.get("db.username"))
    logger.debug("db port: %s", config.get("db.port"))
    logger.debug("db name: %s", config.get("db.name"))
    logger.debug("db password: %s", config.get("db.password"))


    with session_scope(config) as db_session:
        while True:
            try:
                db_session.execute("select 1")
                logger.debug("Database ready!")
                break
            except OperationalError:
                logger.debug("Waiting for database readiness")
                sleep(3)

        logger.debug("Creating database schema and seeding with data")
        Base.metadata.create_all(db_session.get_bind())

        seed_db(db_session, zones.Zones, ZONES)
        seed_db(db_session, devices.Devices, DEVICES)
        seed_db(db_session, device_zones.DeviceZones, DEVICE_ZONES)
