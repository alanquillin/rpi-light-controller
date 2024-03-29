#!/usr/bin/env python
import argparse
import os
import sys
import time
import logging

import requests

ENV_PREFIX = ''

def get_env(var, default=None, con_fn=None):
    val = os.environ.get(ENV_PREFIX + var, default)
    if con_fn:
        val = con_fn(val)
    return val

def to_bool(val):
    return bool(val)

log_level_str = get_env("LOG_LEVEL", "INFO")
log_level = getattr(logging, log_level_str, logging.INFO)

LOG_FMT = "%(levelname)-8s: %(asctime)-15s [%(name)s]: %(message)s"
root_logger = logging.getLogger()
root_logger.setLevel(log_level)
if root_logger.handlers:
    for log_handler in root_logger.handlers:
        log_handler.setFormatter(logging.Formatter(fmt=LOG_FMT))
logging.basicConfig(level=log_level, format=LOG_FMT)

LOG = logging.getLogger("monitor")

DB_DATE_FORMAT = '%H:%M:%S'
SYSTEM_PROGRAM_TIMER = 'timer'

req_details = {}

host = 'localhost'
port = 5000
use_ssl = False
ssl_key = ''
ssl_cert = ''
ssl_ca = ''
api_prefix = '/api/v1'

def shutdown(*args, **kwargs):
    sys.exit(0)


def get_zones():
    return get(f"{api_prefix}/zones").json()


def turn_zone_on(zone_num):
    post(f"{api_prefix}/zones/{zone_num}/on")


def turn_zone_off(zone_num):
    post(f"{api_prefix}/zones/{zone_num}/off")


def ping():
    try:
        get('/health')
        return True
    except Exception as ex:
        print(ex)
        return False

def req(fn):
    def wrapper(uri, **kwargs):
        url = '{0}://{1}:{2}{3}'.format('https' if use_ssl else 'http', host, port, uri)
        if use_ssl:
            kwargs['verify'] = ssl_ca
            kwargs['cert'] = (ssl_cert, ssl_key)
        LOG.debug(url)
        return fn(url, **kwargs)
    return wrapper

@req
def get(uri, **kwargs):
    return requests.get(uri, **kwargs)

@req
def post(uri, **kwargs):
    return requests.post(uri, **kwargs)


def get_time(t):
    dt = '%s/%s/%s %s' % (now.tm_mon, now.tm_mday, now.tm_year, t)
    format = '%m/%d/%Y {}'.format(DB_DATE_FORMAT)
    return time.strptime(dt, format)

if __name__ == '__main__':
    disabled = get_env('DISABLE_MONITOR', False, to_bool)

    if disabled:
        LOG.warning("Monitor is disabled.  Shutting down")
        shutdown()

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--host', help='hostname for the light controller API')
    parser.add_argument('--port', help='port for the light controller API')
    parser.add_argument('--no-secure', help='Flag to use use HTTP instead of HTTPS', action='store_true')
    parser.add_argument('--ssl-key', help='')
    parser.add_argument('--ssl-cert', help='')
    parser.add_argument('--ssl-ca', help='')
    parser.add_argument('--no-loop', help='', action='store_true')
    parser.add_argument('--log-level', help='')
    parser.add_argument('--interval', help='The interval in seconds to wait between zone checks.  Default is 60 sec.')

    args = parser.parse_args()

    host = args.host
    if not host:
        host = get_env('HOST', 'localhost')

    port = args.port
    if not port:
        port = get_env('PORT', 5000, int)

    no_secure = args.no_secure
    if no_secure:
        use_ssl = False
    else:
        use_ssl = get_env('SSL_ENABLE', False)

    ssl_key = args.ssl_key
    if not ssl_key:
        ssl_key = get_env('SSL_KEY_FILE', '/var/lib/christmas-lts/monitor.key')

    ssl_cert = args.ssl_cert
    if not ssl_cert:
        ssl_cert = get_env('SSL_CERT_FILE', '/var/lib/christmas-lts/monitor.cert')

    ssl_ca = args.ssl_ca
    if not ssl_ca:
        ssl_ca = get_env('SSL_CA_FILE', '/var/lib/christmas-lts/ca.cert')
    
    internal = args.interval
    if not internal:
        interval = get_env('INTERVAL', 60, int)

    LOG.info('Host: %s' % host)
    LOG.info('Port: %s' % port)
    LOG.info('Use SSL: %s'%  use_ssl)
    if use_ssl:
        LOG.info('SSL:\n\tKey: %s\n\tCert: %s\n\tCA: %s' % (ssl_key, ssl_cert, ssl_ca))
    LOG.info('Log Level: %s' % log_level_str)

    zone_states = {}
    last_conn_failed=False
    init_conn_att=False
    try:
        while True:
            if not ping():
                LOG.warning("Unable to communicate with the back end service... waiting and will try again.")
                init_conn_att=True
                last_conn_failed=True
                time.sleep(10)
                continue
            
            if last_conn_failed or not init_conn_att:
                LOG.info("Communication to backend service (re)established")
                last_conn_failed=False
            init_conn_att=True

            zones = get_zones()

            for zone in zones:
                zone_num = zone['id']

                if zone['program'] != SYSTEM_PROGRAM_TIMER:
                    LOG.debug("Zone %s has program set to %s, skipping", zone_num, zone["program"])
                    continue
                
                state = zone["state"].lower()
                expected_state = zone.get("expectedState", "").lower()

                LOG.debug("Checking zone %s state:  Current = %s, Expected = %s", zone_num, state, expected_state)

                if expected_state == "on":
                    LOG.debug('Turning lights for zone %s on' % zone_num)
                    turn_zone_on(zone_num)
                else:
                    LOG.debug('Turning lights for zone %s off' % zone_num)
                    turn_zone_off(zone_num)

            time.sleep(interval)
            if args.no_loop:
                LOG.info("no-loop param is set, exiting.")
                break

    except (KeyboardInterrupt, SystemExit):
        LOG.error('Caught KeyboardInterrupt, initiate shutdown')
    except Exception:
        LOG.exception('Caught unhandled exception')
    finally:
        shutdown()
