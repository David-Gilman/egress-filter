
import logging_helper
from _metadata import __version__, __authorshort__, __module_name__
from resources import templates, schema
from configurationutil import Configuration, cfg_params

logging = logging_helper.setup_logging()

# Register Config details (These are expected to be overwritten by an importing app)
cfg_params.APP_NAME = __module_name__
cfg_params.APP_AUTHOR = __authorshort__
cfg_params.APP_VERSION = __version__

# Set the config initialisation parameters
DNS_LOOKUP_CFG = u'dns_lookup'
TEMPLATE = templates.dns_lookup

# Constants for accessing config items
REDIRECT_HOSTNAME = u'redirect_hostname'
REDIRECT_ADDRESS = u'address'
ACTIVE = u'active'


class NoActiveRecordForHost(Exception):
    pass


def get_redirection_config(active_only=False):

    # Retrieve configuration instance
    cfg = Configuration()

    # Register configuration
    cfg.register(config=DNS_LOOKUP_CFG,
                 config_type=cfg_params.CONST.json,
                 template=TEMPLATE,
                 schema=schema.dns_lookup)

    dns_redirections = cfg.find(DNS_LOOKUP_CFG, [(ACTIVE, True)]) if active_only else cfg[DNS_LOOKUP_CFG]
    logging.debug(dns_redirections)

    # Return a copy so that modifications of the retrieved do not get modified in config unless explicitly requested!
    return dns_redirections.copy()


def get_active_redirection_config():
    return get_redirection_config(active_only=True)


def get_active_redirect_record_for_host(host):

    active_redirects = get_active_redirection_config()

    if host not in active_redirects:
        raise NoActiveRecordForHost(host)

    return active_redirects[host]


def get_redirect_hostname_for_host(host):
    redirect_hostname = get_active_redirect_record_for_host(host)[REDIRECT_HOSTNAME]

    if not redirect_hostname:
        raise NoActiveRecordForHost(u'Active record, but no hostname redirection for {host}'.format(host=host))

    return redirect_hostname
