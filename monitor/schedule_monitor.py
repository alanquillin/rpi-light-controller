#!/usr/bin/env python
import argparse
import os
import sys
import time
import logging

import requests

def get_env(var, default=None, con_fn=None):
    val = os.environ.get(ENV_PREFIX + var, default)
    if con_fn:
        val = con_fn(val)
    return val


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

ENV_PREFIX = ''
DB_DATE_FORMAT = '%H:%M:%S'
SYSTEM_PROGRAM_TIMER = 'timer'

req_details = {}

host = 'localhost'
port = 5000
use_ssl = False
ssl_key = ''
ssl_cert = ''
ssl_ca = ''





def shutdown(*args, **kwargs):
    sys.exit(0)


def get_zones():
    return get('/zones').json()


def turn_zone_on(zone_num):
    post(f"/zones/{zone_num}/on")


def turn_zone_off(zone_num):
    post(f"/zones/{zone_num}/off")


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
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--host', help='hostname for the christma lights service')
    parser.add_argument('--port', help='port for the christma lights service')
    parser.add_argument('--no-secure', help='Flag to use use HTTP instead of HTTPS', action='store_true')
    parser.add_argument('--ssl-key', help='Flag to use use HTTP instead of HTTPS')
    parser.add_argument('--ssl-cert', help='Flag to use use HTTP instead of HTTPS')
    parser.add_argument('--ssl-ca', help='Flag to use use HTTP instead of HTTPS')
    parser.add_argument('--no-loop', help='', action='store_true')
    parser.add_argument('--debug', help='', action='store_true')
    parser.add_argument('--interval', help='The interval in seconds to wait between zone checks')

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
    try:
        while True:
            if not ping():
                LOG.warning("Unable to communicate with the back end service... waiting and will try again.")
                time.sleep(10)
                continue

            zones = get_zones()

            for zone in zones:
                if zone['program'] != SYSTEM_PROGRAM_TIMER:
                    LOG.info("Zone %s has program set to %s, skipping", zone["id"], zone["program"])
                    continue
                
                zone_num = zone['id']
                now = time.localtime()
                start = get_time(zone['on'])
                end = get_time(zone['off'])

                if start < now < end:
                    LOG.debug('Turning lights for zone %s on' % zone_num)
                    turn_zone_on(zone_num)
                else:
                    LOG.debug('Turning lights for zone %s off' % zone_num)
                    turn_zone_off(zone_num)

            time.sleep(interval)
            if args.no_loop:
                break

    except (KeyboardInterrupt, SystemExit):
        LOG.error('Caught KeyboardInterrupt, initiate shutdown')
    except Exception:
        LOG.exception('Caught unhandled exception')
    finally:
        shutdown()
