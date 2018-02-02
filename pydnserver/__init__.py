
# Get module version
from ._metadata import __version__

# Import key items from module
from .dns_server import DNSServer
from .dns_query import DNSQuery

from .config import dns_lookup
from .config import dns_forwarders

# Set default logging handler to avoid "No handler found" warnings.
from logging import NullHandler, getLogger
getLogger(__name__).addHandler(NullHandler())
