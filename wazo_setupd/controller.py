# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging
import signal

from functools import partial
from xivo import plugin_helpers
from xivo.consul_helpers import ServiceCatalogRegistration
from .rest_api import api, CoreRestApi

logger = logging.getLogger(__name__)


class Controller:

    def __init__(self, config):
        self._service_discovery_args = [
            'wazo-setupd',
            config.get('uuid'),
            config['consul'],
            config['service_discovery'],
            config['bus'],
            lambda: True,
        ]
        self.rest_api = CoreRestApi(config)
        plugin_helpers.load(
            namespace='wazo_setupd.plugins',
            names=config['enabled_plugins'],
            dependencies={
                'api': api,
                'config': config,
            }
        )

    def run(self):
        logger.info('wazo-setupd starting...')
        signal.signal(signal.SIGTERM, partial(_sigterm_handler, self))
        try:
            with ServiceCatalogRegistration(*self._service_discovery_args):
                self.rest_api.run()
        finally:
            logger.info('wazo-setupd stopping...')

    def stop(self, reason):
        logger.warning('Stopping wazo-setupd: %s', reason)
        self.rest_api.stop()


def _sigterm_handler(controller, signum, frame):
    controller.stop(reason='SIGTERM')
