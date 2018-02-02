# encoding: utf-8

import socket
import logging_helper
from classutils.thread_pool import ThreadPool
from .dns_query import DNSQuery

logging = logging_helper.setup_logging()


class DNSServer(ThreadPool):

    DEFAULT_INTERFACE = u'0.0.0.0'
    DEFAULT_PORT = 53

    def __init__(self,
                 interface=DEFAULT_INTERFACE,
                 port=DEFAULT_PORT,
                 *args,
                 **kwargs):

        super(DNSServer, self).__init__(*args,
                                        **kwargs)

        self.interface = interface
        self.port = port

        self.server_socket = socket.socket(socket.AF_INET,
                                           socket.SOCK_DGRAM)
        self.server_socket.settimeout(1)

        self._stop = True  # Set termination flag
        self._main_async_response = None

    def start(self):

        logging.info(u'Starting DNS Server on {int}:{port}...'.format(int=self.interface,
                                                                      port=self.port))

        # Run initialisation steps here
        self._stop = False

        try:
            self.server_socket.bind((self.interface,
                                     self.port))
            logging.debug(u'DNS Server socket bound')

        except Exception as err:
            logging.exception(err)
            logging.error(u'DNS Server failed to start, failed binding socket to destination '
                          u'({destination}:{port})'.format(destination=self.interface,
                                                           port=self.port))

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

        logging.info(u'DNS Server Stopped')

    def _main_loop(self):

        logging.info(u'DNS ({dns}): Waiting for lookup requests'.format(dns=self.interface))

        while not self._stop:
            try:
                data, address = self.server_socket.recvfrom(1024)

                # Pass item to worker thread
                self.submit_task(func=self._query,
                                 kwargs={u'request': data,
                                         u'address': address})

            except socket.timeout:
                continue

    def _query(self,
               request,
               address):
        try:
            logging.debug(address)
            logging.debug(repr(request))

            query = DNSQuery(data=request,
                             client_address=address,
                             interface=self.interface)

            self.server_socket.sendto(query.resolve(), address)

            logging.info(query.message)

        except Exception as err:
            logging.exception(err)

    @property
    def active(self):
        return not self._stop
