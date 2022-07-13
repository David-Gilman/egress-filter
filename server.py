from pydnserver import DNSServer
import logging
import os
from flask import Flask
from allowlist.allow_list import AllowList
from awsclient.sg_client import SGClient
from domaincache.domaincache import DomainCache

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

ip = u'172.31.82.183'  # Set this to the IP address of your network interface.
app = Flask(__name__)
group_id = 'sg-020909fd2c5a43770'


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
    sg_client = SGClient(group_id=group_id)
    domain_cache = DomainCache

    dns = DNSServer(domain_cache=domain_cache, allow_list=allow_list, sg_client=sg_client, interface=ip, port=53)
    dns.start()

    try:
        while True:
            pass

    except KeyboardInterrupt:
        dns.stop()
