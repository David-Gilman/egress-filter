from pydnserver import DNSServer
import logging
import os

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

ip = u'172.31.82.183'  # Set this to the IP address of your network interface.

dns = DNSServer(interface=ip, port=53)
dns.start()

try:
    while True:
        pass

except KeyboardInterrupt:
    dns.stop()
