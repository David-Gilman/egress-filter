# encoding: utf-8

import os
import sys
import socket
import logging_helper
from classutils.thread_pool import ThreadPool
from ipaddress import IPv4Network, IPv4Address, AddressValueError
from networkutil.addressing import get_my_addresses
from .dns_query import DNSQuery
from ._exceptions import DNSQueryFailed
from allowlist.allow_list import AllowList
from awsclient.sg_client import SGClient
from domaincache.domaincache import DomainCache
import time


logging = logging_helper.setup_logging()


def ensure_unicode(s):
    if isinstance(s, str):
        try:
            return s.decode('utf-8')
        except Exception:
            return ''.join([c if ord(c) < 128 else '?' for c in s])
    return s


class DNSServer(ThreadPool):
    DEFAULT_INTERFACE = u'0.0.0.0'
    DEFAULT_PORT = 100

    def __init__(self,
                 allow_list: AllowList,
                 sg_client: SGClient,
                 domain_cache: DomainCache,
                 interface=DEFAULT_INTERFACE,
                 port=DEFAULT_PORT,
                 *args,
                 **kwargs):

        super(DNSServer, self).__init__(*args,
                                        **kwargs)

        self.interface = interface
        self.port = port

        self.server_socket = None

        self._stop = True  # Set termination flag
        self._main_async_response = None

        self.allow_list = allow_list
        self.sg_client = sg_client
        self.domain_cache = domain_cache

    def start(self):

        logging.info(u'Starting DNS Server on {int}:{port}...'.format(int=self.interface,
                                                                      port=self.port))

        if (sys.platform == u'darwin'
                and os.geteuid() != 0
                and self.port <= 1024):
            raise Exception(u'You are running macOS please restart with sudo!')

        # Run initialisation steps here
        self._stop = False

        try:
            self._create_socket()

        except Exception as err:
            logging.exception(ensure_unicode(err.message))
            logging.error(u'DNS Server failed to start, failed binding socket to destination '
                          u'({destination}:{port})'.format(destination=self.interface,
                                                           port=self.port))
            if 'win' in sys.platform:
                logging.error(u'The Internet Connection Sharing (ICS) service may have hijacked the port.')

            self._stop = True

        if not self._stop:
            logging.info(u'DNS Server Started on {int}:{port}!'.format(int=self.interface,
                                                                       port=self.port))

            # Create pool and Run Main loop
            self.create()
            self._main_async_response = self.submit_task(self._main_loop)

    def stop(self):

        logging.info(u'Stopping DNS Server, waiting for processes to complete...')

        # Signal loop termination
        self._stop = True

        # Retrieve & raise any exceptions from thread!
        if self._main_async_response is not None:
            self._main_async_response.get(timeout=60)

        self._main_async_response = None

        self.destroy()

        self.server_socket = None

        logging.info(u'DNS Server Stopped')

    def _main_loop(self):

        logging.info(u'DNS ({dns}): Waiting for lookup requests'.format(dns=self.interface))

        while not self._stop:
            if int(time.time()) % 60 == 0:
                self.submit_task(self._update_sg())

            try:
                data, address = self.server_socket.recvfrom(1024)

                # Pass item to worker thread
                self.submit_task(func=self._query,
                                 kwargs={u'request': data,
                                         u'address': address})

            except (socket.timeout, socket.error):
                continue

            except Exception as err:
                logging.error(u'Something went wrong in DNS Server main thread: {err}'.format(err=err))

    def _update_sg(self):
        tbd = self.domain_cache.get_and_del_expired_ips()
        logging.info(tbd)
        logging.info(self.domain_cache.ip_ttls)
        for ip in tbd:
            try:
                self.sg_client.del_rule(str(ip))
            except Exception as e:
                logging.error(e)
                pass

    def _create_socket(self):
        self.server_socket = socket.socket(socket.AF_INET,
                                           socket.SOCK_DGRAM)

        self.server_socket.settimeout(1)

        self.server_socket.bind((self.interface,
                                 self.port))

        logging.debug(u'DNS Server socket bound')

    def _query(self,
               request,
               address):
        try:
            logging.debug(address)
            logging.debug(repr(request))

            # Try to narrow down interface from client address
            # We are assuming a /24 network as this is the most common for LAN's

            # Start with the server interface
            interface = self.interface

            # Get the client network to test our interfaces against
            client_net = IPv4Network(u'{ip}/24'.format(ip=address[0]),
                                     strict=False)

            # Search for an interface address on the same network as the client
            for addr in get_my_addresses():
                try:
                    if IPv4Address(u'{ip}'.format(ip=addr)) in client_net:
                        interface = addr
                        break  # We found a matching address so no point looping through remaining addresses!

                except AddressValueError:
                    pass

            # Create query
            query = DNSQuery(data=request,
                             client_address=address,
                             interface=interface)

            if self.allow_list.is_allowed(u'.'.join(str(query.question.name).split('.')[-3:])):
                logging.info(f'Allowed query: {query.question.name}')
            else:
                raise Exception(f"Not allowed query: {query.question.name}")

            # Make query & Respond to the client
            self.server_socket.sendto(query.resolve(self.sg_client, self.domain_cache), address)

        except DNSQueryFailed as err:
            logging.error(err)

        except Exception as err:
            logging.exception(err)

    @property
    def active(self):
        return not self._stop
