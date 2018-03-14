# encoding: utf-8

import logging_helper
from pydnserver import DNSServer
from configurationutil import Configuration
from future.utils import iteritems
from apiutil.endpoints import Hosts

# Force config load!
Configuration()

logging = logging_helper.setup_logging(level=logging_helper.DEBUG,
                                       log_to_file=False)

# create a domain list where some items have friendly names and some don't!
address_list = [(host_cfg.domain, host_name) for host_name, host_cfg in iteritems(Hosts())]
address_list.insert(1, u'google.co.uk')
address_list.append(u'bbc.co.uk')
address_list.append((u'sky.com', u''))

dns = DNSServer(port=9053)
dns.start()

logging.debug(u'READY')

try:
    from pydnserver.gui.window.dns_config_launcher import DNSConfigLauncherRootWindow
    DNSConfigLauncherRootWindow(zone_address_list=address_list)

    while True:
        pass

except KeyboardInterrupt:
    dns.stop()
