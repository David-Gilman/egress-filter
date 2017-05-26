
import socket
import dns.resolver
import logging_helper
import dns_lookup
import dns_forwarders

logging = logging_helper.setup_logging()


class DNSQueryFailed(Exception):
    pass


class DNSQuery(object):

    def __init__(self,
                 data,
                 interface=None):

        self.data = data
        self.interface = interface if interface is not None else u'default'
        self.message = u''
        self.ip = None
        self.error = u''

    def resolve(self):

        try:
            name = self.__decode_query()

            if name[-1] == u'.':
                name = name[:-1]

            self.message = (u'DNS ({dns}): {name}: ?.?.?.?. '
                            .format(dns=self.interface,
                                    name=name))

            # Handle reverse lookups
            if u'.in-addr.arpa.' in name:
                raise DNSQueryFailed(u'Cannot handle reverse lookups yet!')

            # Check if we have a configured record for requested name
            try:
                redirect_record = dns_lookup.get_active_redirect_record_for_host(name)

            except dns_lookup.NoActiveRecordForHost:
                self.message += u'Forwarding request. '
                address = self.__forward_request(name)
                self.ip = address

            else:
                address = redirect_record[dns_lookup.REDIRECT_ADDRESS]

                if address != u'':  # TODO: Convert this to a None field!
                    if address.lower() == u'default':
                        address = self.interface
                        self.message += (u'Redirecting to default address.'.format(address=address))
                    else:
                        self.message += (u'Redirecting to address.'.format(address=address))

                    self.ip = address

                else:       

                    redirection = redirect_record[dns_lookup.REDIRECT_HOSTNAME]

                    redirected_address = self.__forward_request(redirection)

                    self.message += (u'Redirecting to {redirection}'.format(redirection=redirection))

                    self.ip = redirected_address

            self.message = self.message.replace(u'?.?.?.?', self.ip)

        except DNSQueryFailed as error:
            self.error = error
            return self.__bad_reply()

        else:
            return self.__reply()

    def __decode_query(self):

        domain = ''
        optype = (ord(self.data[2]) >> 3) & 15   # Opcode bits

        if optype == 0:                     # Standard query
            ini = 12
            lon = ord(self.data[ini])
            while lon != 0:
                domain += self.data[ini + 1: ini + lon + 1] + '.'
                ini += lon + 1
                lon = ord(self.data[ini])

        return domain

    def __forward_request(self,
                          name):

        try:
            address = self.__resolve_name_using_dns_resolver(name)

        except (dns_forwarders.NoForwardersConfigured, DNSQueryFailed):
            self.message += u'No passthrough nameservers. '
            address = self.__resolve_name_using_socket(name)

        return address

    def __resolve_name_using_socket(self,
                                    name):

        # TODO: Ought to add some basic checking of name here

        try:
            address = socket.gethostbyname(name)
            self.message += u"(socket)."

        except socket.gaierror, err:
            raise DNSQueryFailed(u'Resolve using socket failed: {err}'.format(err=err))

        else:
            return address

    def __resolve_name_using_dns_resolver(self,
                                          name):

        resolver = dns.resolver.Resolver()
        resolver.timeout = 1
        resolver.lifetime = 3
        resolver.nameservers = dns_forwarders.get_forwarders_by_interface(self.interface)

        try:
            result = resolver.query(qname=name,
                                    rdtype=u"A",
                                    source=self.interface)

            address = result[0].address

            self.message += u'(dns.resolver). '

            logging.debug(u'Address for {name} via dns.resolver from {source}: {address}'.format(name=name,
                                                                                                 source=self.interface,
                                                                                                 address=address))

        except (IndexError, dns.exception.DNSException, dns.exception.Timeout) as err:
            self.message += u'(dns.resolver failed). '
            raise DNSQueryFailed(u'dns.resolver failed: {err}'.format(err=err))

        else:
            return address

    def __reply(self,
                ip=None):

        ip = ip if ip is not None else self.ip

        packet = ''
        packet += self.data[:2] + "\x81\x80"
        packet += self.data[4:6] + self.data[4:6] + '\x00\x00\x00\x00'      # Questions and Answers Counts
        packet += self.data[12:]                                            # Original Domain Name Question
        packet += '\xc0\x0c'                                                # Pointer to domain name
        packet += '\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04'                # Response type, ttl and resource data length -> 4 bytes
        packet += str.join('', map(lambda x: chr(int(x)), ip.split('.')))   # 4 bytes of IP

        return packet

    def __bad_reply(self):
            # TODO: Figure out how to return rcode 2 or 3
            # DNS Response Code | Meaning
            # ------------------+-----------------------------------------
            # RCODE:2           | Server failed to complete the DNS request
            # RCODE:3           | this code signifies that the domain name
            #                   | referenced in the query does not exist.
            logging.warning(self.error)
            # For now, return localhost,
            # which should fail on the calling machine
            return self.__reply(ip=u'127.0.0.1')
