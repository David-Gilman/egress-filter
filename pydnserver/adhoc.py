# encoding: utf-8

import os
import sys
import logging_helper
from configurationutil import Configuration, cfg_params
from pydnserver import DNSServerRootWindow, __version__, __authorshort__, __module_name__
from future.utils import iteritems
from apiutil.endpoints import APIConfig


# Register Config details (These are expected to be overwritten by an importing app)
cfg_params.APP_NAME = __module_name__
cfg_params.APP_AUTHOR = __authorshort__
cfg_params.APP_VERSION = __version__
Configuration()  # Force config load!

logging = logging_helper.setup_logging(level=logging_helper.INFO,
                                       log_to_file=False)

dns_port = 8053 if sys.platform == u'darwin' and os.geteuid() != 0 else 53

# create a domain list where some items have friendly names and some don't!
address_list = [(host_cfg.domain, host_name) for host_name, host_cfg in iteritems(APIConfig().hosts)]
address_list.insert(1, u'google.co.uk')
address_list.append(u'bbc.co.uk')
address_list.append((u'sky.com', u''))

dns = DNSServerRootWindow(server_kwargs=dict(port=dns_port),
                          zone_address_list=address_list)
