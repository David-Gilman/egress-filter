
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
DNS_SERVERS_CFG = u'dns_servers'
TEMPLATE = templates.dns_forwarders


class NoForwardersConfigured(Exception):
    pass


def get_all_forwarders(interface=None):

    # Retrieve configuration instance
    cfg = Configuration()

    # Register configuration
    cfg.register(config=DNS_SERVERS_CFG,
                 config_type=cfg_params.CONST.json,
                 template=TEMPLATE,
                 schema=schema.dns_forwarders)

    if interface is not None:
        key = u'{c}.{n}'.format(c=DNS_SERVERS_CFG,
                                n=interface)

        try:
            dns_forwarders = cfg[key]

        except KeyError as err:
            raise NoForwardersConfigured(err)

        else:
            if len(dns_forwarders) == 0:
                raise NoForwardersConfigured(u'No Forwarders have been configured for {int}'.format(int=interface))

    else:
        dns_forwarders = cfg[DNS_SERVERS_CFG]

    logging.debug(dns_forwarders)

    # Return a copy so that modifications of the retrieved do not get modified in config unless explicitly requested!
    return dns_forwarders[:] if type(dns_forwarders) == list else dns_forwarders.copy()


def get_forwarders_by_interface(interface):
    return get_all_forwarders(interface=interface)


# TODO: Add default forwarder config
