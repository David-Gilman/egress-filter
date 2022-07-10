from pydnserver import DNSServer
import logging
import os
from flask import Flask
from allowlist.allow_list import AllowList
from awsclient.sg_client import SGClient

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

ip = u'172.31.82.183'  # Set this to the IP address of your network interface.
app = Flask(__name__)


@app.route('/domains/', methods=['GET'])
def domain_get_all():
    return 'hi'


@app.route('/domains/<domain>', methods=['GET'])
def domain_get(domain):
    return 'hi'


@app.route('/domains/<domain>', methods=['POST'])
def domain_add(domain):
    pass


@app.route('/domains/<domain>', methods=['DELETE'])
def domain_delete(domain):
    return 'Hello'


if __name__ == '__main__':
    allow_list = AllowList({u'google.com.', u'aws.com.', u'microsoft.com.'})

    dns = DNSServer(allow_list=allow_list, interface=ip, port=53)
    dns.start()

    try:
        while True:
            pass

    except KeyboardInterrupt:
        dns.stop()
