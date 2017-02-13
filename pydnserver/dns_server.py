
import socket
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool
import logging_helper
from dns_query import DNSQuery

logging = logging_helper.setup_logging()


class DNSServer(object):

    def __init__(self,
                 interface=None,
                 port=53,
                 threads=cpu_count()):

        self.interface = interface
        self.port = port

        self.pool = ThreadPool(processes=threads if threads > 1 else 2)

        self.server_socket = socket.socket(socket.AF_INET,
                                           socket.SOCK_DGRAM)
        self.server_socket.settimeout(1)

        self.__stop = True  # Set termination flag

    def start(self):

        logging.info(u'Starting DNS Server on {int}:{port}...'
                     .format(int=self.interface,
                             port=self.port))

        # Run initialisation steps here
        self.__stop = False

        try:
            self.server_socket.bind((self.interface,
                                     self.port))
            logging.debug(u'DNS Server socket bound')

        except Exception as err:

            logging.exception(err)
            logging.error(u'DNS Server failed to start, '
                          u'failed binding socket to destination '
                          u'({destination}:{port})'
                          .format(destination=self.interface,
                                  port=self.port))

            self.__stop = True

        if not self.__stop:
            logging.info(u'DNS Server Started on {int}:{port}!'
                         .format(int=self.interface,
                                 port=self.port))

            # Run Main loop
            self.pool.apply_async(func=self.__main_loop)

    def stop(self):

        logging.info(u'Stopping DNS Server, '
                     u'waiting for processes to complete...')

        # Signal loop termination
        self.__stop = True

        # Wait for running processes to complete
        self.pool.close()
        self.pool.join()

        logging.info(u'DNS Server Stopped')

    def __main_loop(self):

        logging.info(u'DNS ({dns}): Waiting for lookup requests'
                     .format(dns=self.interface))

        while not self.__stop:

            try:
                data, address = self.server_socket.recvfrom(1024)

                # Pass item to worker thread
                self.pool.apply_async(func=self.__worker,
                                      kwds={u'request': data,
                                            u'address': address})

            except socket.timeout:
                continue

    def __worker(self,
                 request,
                 address):
        try:
            logging.debug(address)
            logging.debug(repr(request))

            query = DNSQuery(data=request,
                             interface=self.interface)

            self.server_socket.sendto(query.resolve(), address)

            logging.info(query.message)

        except Exception as err:
            logging.exception(err)

    @property
    def active(self):
        return not self.__stop


if __name__ == u'__main__':

    dns = DNSServer(interface=u'172.20.0.5', port=9053)
    dns.start()

    logging.debug(u'READY')

    try:
        while True:
            pass

    except KeyboardInterrupt:
        dns.stop()
