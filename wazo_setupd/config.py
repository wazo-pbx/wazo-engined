# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import argparse
import os

from xivo.chain_map import ChainMap
from xivo.config_helper import read_config_file_hierarchy
from xivo.xivo_logging import get_log_level_by_name

_CERT_FILE = '/usr/share/xivo-certs/server.crt'
_DEFAULT_HTTPS_PORT = 9302
_PID_DIR = '/var/run/wazo-setupd'

_DEFAULT_CONFIG = {
    'config_file': '/etc/wazo-setupd/config.yml',
    'debug': False,
    'extra_config_files': '/etc/wazo-setupd/conf.d',
    'log_file': '/var/log/wazo-setupd.log',
    'log_level': 'info',
    'pid_file': os.path.join(_PID_DIR, 'wazo-setupd.pid'),
    'self_stop_delay': 10.0,
    'auth': {
        'host': 'localhost',
        'port': 9497,
        'verify_certificate': _CERT_FILE,
    },
    'bus': {
        'username': 'guest',
        'password': 'guest',
        'host': 'localhost',
        'port': 5672,
        'exchange_name': 'xivo',
        'exchange_type': 'topic',
        'exchange_headers_name': 'wazo-headers',
    },
    'confd': {
        'host': 'localhost',
        'port': 9486,
        'verify_certificate': _CERT_FILE,
    },
    'consul': {
        'scheme': 'https',
        'host': 'localhost',
        'port': 8500,
        'verify': '/usr/share/xivo-certs/server.crt',
    },
    'rest_api': {
        'listen': '0.0.0.0',
        'port': _DEFAULT_HTTPS_PORT,
        'certificate': _CERT_FILE,
        'private_key': '/usr/share/xivo-certs/server.key',
        'cors': {
            'enabled': True,
            'allow_headers': ['Content-Type', 'X-Auth-Token'],
        },
    },
    'service_discovery': {
        'advertise_address': 'auto',
        'advertise_address_interface': 'eth0',
        'advertise_port': _DEFAULT_HTTPS_PORT,
        'enabled': True,
        'ttl_interval': 30,
        'refresh_interval': 27,
        'retry_interval': 2,
        'extra_tags': [],
    },
    'enabled_plugins': {
        'api': True,
        'config': True,
        'setup': True,
        'status': True,
    },
}


def load_config(args):
    cli_config = _parse_cli_args(args)
    file_config = read_config_file_hierarchy(ChainMap(cli_config, _DEFAULT_CONFIG))
    reinterpreted_config = _get_reinterpreted_raw_values(cli_config, file_config, _DEFAULT_CONFIG)
    return ChainMap(reinterpreted_config, cli_config, file_config, _DEFAULT_CONFIG)


def _get_reinterpreted_raw_values(*configs):
    config = ChainMap(*configs)
    return dict(
        log_level=get_log_level_by_name('debug' if config['debug'] else config['log_level']),
    )


def _parse_cli_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config-file', action='store', help='The path to the config file')
    parser.add_argument('-d', '--debug', action='store_true', help='Log debug mesages. Override log_level')
    parser.add_argument('-u', '--user', action='store', help='The owner of the process')
    parsed_args = parser.parse_args()

    result = {}
    if parsed_args.config_file:
        result['config_file'] = parsed_args.config_file
    if parsed_args.debug:
        result['debug'] = parsed_args.debug
    if parsed_args.user:
        result['user'] = parsed_args.user

    return result
