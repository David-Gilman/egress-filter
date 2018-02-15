# encoding: utf-8

import logging_helper
from pydnserver import DNSServer
from configurationutil import Configuration

# Force config load!
Configuration()

logging = logging_helper.setup_logging(level=logging_helper.DEBUG,
                                       log_to_file=False)


dns = DNSServer(port=9053)
dns.start()

logging.debug(u'READY')

try:
    from pydnserver.gui.window.dns_config_launcher import DNSConfigLauncherRootWindow
    DNSConfigLauncherRootWindow()

    while True:
        pass

except KeyboardInterrupt:
    dns.stop()
