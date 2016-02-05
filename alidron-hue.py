# Copyright (c) 2015-2016 Contributors as noted in the AUTHORS file
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import logging
import os
import signal
import socket
import sys
from functools import partial
from phue import Bridge

from isac import IsacNode, IsacValue
from isac.tools import green

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.WARNING)

class AlidronHue(object):

    def __init__(self, bridges):
        self.isac_node = IsacNode('alidron-hue')
        green.signal(signal.SIGTERM, partial(self._sigterm_handler))
        green.signal(signal.SIGINT, partial(self._sigterm_handler))

        self.bridges = bridges
        self.signals = {}

        self.sync_signals()

    def sync_signals(self):
        for bridge in self.bridges.values():
            for light in bridge.get_light().values():
                light_obj = bridge[str(light['name'])]
                for prop in light['state']:
                    if prop == 'bri':
                        prop = 'brightness'
                    elif prop == 'sat':
                        prop = 'saturation'

                    uri = self.make_uri(light_obj, prop)
                    if uri not in self.signals:
                        self.make_value(uri, light_obj, prop)

    def make_uri(self, light_obj, prop):
        return 'hue://%s/%s' % (light_obj.name, str(prop))

    def make_value(self, uri, light_obj, prop):
        iv = IsacValue(
            self.isac_node, uri,
            initial_value=getattr(light_obj, prop),
            survey_last_value=False,
            survey_static_tags=False
        )
        iv.observers += self.value_update

        self.signals[uri] = {
            'isac_value': iv,
            'light_object': light_obj,
            'property': prop,
        }

        print '>>> Registered', uri

    def value_update(self, iv, value, timestamp, tags):
        print 'Receveid update for', iv.uri, ':', value, tags

        if 'transitiontime' in tags:
            old_trt = self.signals[iv.uri]['light_object'].transitiontime
            self.signals[iv.uri]['light_object'].transitiontime = tags['transitiontime']

        setattr(
            self.signals[iv.uri]['light_object'],
            self.signals[iv.uri]['property'],
            value
        )

        if 'transitiontime' in tags:
            self.signals[iv.uri]['light_object'].transitiontime = old_trt

    def serve_forever(self):
        try:
            self.isac_node.serve_forever()
        except (KeyboardInterrupt, SystemExit):
            logger.info('Stopping')
            return

    def stop(self):
        self.isac_node.shutdown()
        green.sleep(2)

    def _sigterm_handler(self):
        logger.info('Received SIGTERM signal, exiting')
        self.stop()
        logger.info('Exiting')
        sys.exit(0)

def find_hue_bridges_ip(timeout=1.0):
    # uPnP discovery method with SSDP
    # Could alternatively use portal discovery method (https://www.meethue.com/api/nupnp), see https://github.com/allanbunch/beautifulhue/pull/2/files#diff-bc9a9a6290c43731b439f5a4fdcc357bR60
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    sock.settimeout(timeout)
    sock.sendto(
        'M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: "ssdp:discover"\r\nMX: 2\r\nST: ssdp:all\r\n\r\n',
        ('239.255.255.250', 1900)
    )

    found = []
    try:
        while True:
            data, from_ = sock.recvfrom(4096)
            if 'hue-bridgeid' in [line.split(':')[0] for line in data.split('\r\n')]:
                ip = from_[0]
                if ip not in found:
                    found.append(ip)
                    yield from_[0]

    except socket.timeout:
        return

def main():
    bridges = {}
    config_file_path = os.path.join(os.getcwd(), 'user', '.python_hue')
    for ip in find_hue_bridges_ip():
        bridge = Bridge(ip=ip, config_file_path=config_file_path)
        bridges[ip] = bridge

    ahue = AlidronHue(bridges)
    try:
        ahue.serve_forever()
    finally:
        ahue.stop()

if __name__ == '__main__':
    main()
