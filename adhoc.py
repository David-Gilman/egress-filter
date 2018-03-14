# encoding: utf-8

import logging_helper
from pydnserver import DNSServer
from configurationutil import Configuration
from networkutil.endpoint_config import Endpoints

# Force config load!
Configuration()

logging = logging_helper.setup_logging(level=logging_helper.DEBUG,
                                       log_to_file=False)

# create a domain list where some items have friendly names and some don't!
address_list = [endpoint.hostname for endpoint in Endpoints()]

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
