# encoding: utf-8

import sys
import socket
import dns.resolver
from dns.message import from_wire, make_response
from dns.rcode import NXDOMAIN
import logging_helper
from ipaddress import IPv4Address, IPv4Network, AddressValueError, ip_address
from .config import dns_lookup, dns_forwarders
from ._exceptions import DNSQueryFailed

logging = logging_helper.setup_logging()

'81a70100000100000000000009676574706f636b65740363646e076d6f7a696c6c61036e657400001c0001'
"\x81\xa7\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x09\x67\x65\x74" \
"\x70\x6f\x63\x6b\x65\x74\x03\x63\x64\x6e\x07\x6d\x6f\x7a\x69\x6c" \
"\x6c\x61\x03\x6e\x65\x74\x00\x00\x1c\x00\x01"

"\x81\xa7\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x09\x67\x65\x74" \
"\x70\x6f\x63\x6b\x65\x74\x03\x63\x64\x6e\x07\x6d\x6f\x7a\x69\x6c" \
"\x6c\x61\x03\x6e\x65\x74\x00\x00\x1c\x00\x01"


def move_address_to_another_network(address,
                                    network,
                                    netmask):

    address = ip_address(unicode(address))
    target_network = IPv4Network(u'{ip}/{netmask}'.format(ip=network,
                                                          netmask=netmask),
                                 strict=False)

    network_bits = int(target_network.network_address)
    interface_bits = int(address) & int(target_network.hostmask)

    target_address = network_bits | interface_bits

    return ip_address(target_address)


class DNSQuery(object):

    def __init__(self,
                 data,
                 client_address=None,
                 interface=None):

        self.data = data
        self.decoded = from_wire(data)
        self.question = self.decoded.question[0]
        # .question[0].rdtype=
        #   covers=0
        #   deleting=None
        #   items=[]
        #   name=www.google.com ['www','google','com','']
        #   rdclass=1
        #   rdtype=28
        #   ttl=0

        self.client_address = client_address
        self.interface = interface if interface is not None else u'default'
        self.message = u''
        self._ip = None
        self.error = u''
        # TODO: Handle IPV6, or at least throw an appropriate error if AAAA is received.

    @property
    def ip(self):
        return self._ip

    @ip.setter
    def ip(self,
           ip):
        self._ip = IPv4Address(u'{ip}'.format(ip=ip))

    def resolve(self):

        name = self.question.name
        self.message = u'DNS ({dns}): {name}: ?.?.?.?. '.format(dns=self.interface,
                                                                name=self.question.name)

        # Handle reverse lookups
        if u'.in-addr.arpa.' in name:
            # TODO: Can we not just forward these?  No will return host not IP?
            self.error = u'Cannot handle reverse lookups yet!'
            return self._bad_reply()

        logging.debug(u'resolve name: {h}'.format(h=name))

        # Check if we have a locally configured record for requested name
        try:
            redirect_record = dns_lookup.get_active_redirect_record_for_host(name.to_text())
            logging.debug(u'redirect record: {r}'.format(r=redirect_record))

        except dns_lookup.NoActiveRecordForHost:
            # Forward request
            self.message += u'Forwarding request. '
            answer = self._forward_request(name)
            try:
                answer.response.id = self.decoded.id
            except AttributeError:
                ip = 'NXDOMAIN'  # Don't know this for sure
                encoded = answer.to_wire()
            else:
                ip = answer.response.answer[0].items[0]
                encoded = answer.response.to_wire()
        else:
            # Attempt to resolve locally
            answer = self._resolve_request_locally(redirect_record)
            ip = answer.answer[0].items[0]
            encoded = answer.to_wire()

        self.message = self.message.replace(u'?.?.?.?', str(ip))

        return encoded

    def _resolve_request_locally(self,
                                 redirect_host):

        redirection = redirect_host[dns_lookup.REDIRECT_HOST]

        if redirection.lower() == u'default':
            if self.interface == u'0.0.0.0':  # This string is the DEFAULT_INTERFACE constant of DNSServer object!
                self.error = u'Cannot resolve default as client interface could not be determined!'
                return self._bad_reply()

            redirection = self.interface
            self.message += (u'Redirecting to default address. ({address}) '.format(address=redirection))

        elif '/' in redirection:
            if self.interface == u'0.0.0.0':  # This string is the DEFAULT_INTERFACE constant of DNSServer object!
                self.error = (u'Cannot resolve {redirection} as client interface could not be determined!'
                              .format(redirection=redirection))
                return self._bad_reply()

            address, netmask = redirection.split('/')
            redirection = move_address_to_another_network(address=address,
                                                          network=self.interface,
                                                          netmask=netmask)
            self.message += (u'Redirecting to {address}. '.format(address=redirection))

        # Check whether we already have an IP (A record)
        # Note: For now we only support IPv4
        try:
            IPv4Address(u'{ip}'.format(ip=redirection))

        except AddressValueError:
            # Attempt to resolve CNAME
            redirected_address = self._forward_request(redirection)

        else:
            # We already have the A record
            redirected_address = redirection

        self.message += (u'Redirecting to {redirection} '.format(redirection=redirection))

        self.ip = redirected_address

        # Use of make_response and appending rrset taken from
        # https://programtalk.com/python-examples/dns.message.make_response/
        response = make_response(self.decoded)
        answer = dns.rrset.from_text(str(self.decoded.question[0].name),  # name
                                     600,                                 # ttl
                                     self.decoded.question[0].rdclass,    # rdclass
                                     self.decoded.question[0].rdtype,     # rdtype
                                     redirected_address)                  # *text_rdatas
        response.answer.append(answer)

        return response

    def _forward_request(self,
                         name):

        try:
            response = self._resolve_name_using_dns_resolver(name)

        except (dns_forwarders.NoForwardersConfigured, DNSQueryFailed) as err:
            self.message += u'No forwarders found for request. '
            response = dns.message.make_response(self.decoded)
            response.set_rcode(NXDOMAIN)

        return response

    def _resolve_name_using_socket(self,
                                   name):

        # TODO: Ought to add some basic checking of name here

        try:
            address = socket.gethostbyname(str(name))
            self.message += u"(socket). "

        except socket.gaierror as err:
            raise DNSQueryFailed(u'Resolve name ({name}) using socket failed: {err} '
                                 .format(name=name,
                                         err=err))

        else:
            return address

    def _resolve_name_using_dns_resolver(self,
                                         name):

        try:
            network = IPv4Network(u'{ip}/24'.format(ip=self.interface),
                                  strict=False)

            forwarders = dns_forwarders.get_forwarders_by_interface(network.with_prefixlen)
            logging.debug(u'Using forwarder config: {fwd} '.format(fwd=forwarders))

        except (dns_forwarders.NoForwardersConfigured,
                dns_forwarders.MultipleForwardersForInterface,
                AddressValueError,
                ValueError):
            forwarders = dns_forwarders.get_default_forwarder()
            logging.debug(u'Using default forwarder config: {fwd} '.format(fwd=forwarders))

        resolver = dns.resolver.Resolver()
        resolver.timeout = 1
        resolver.lifetime = 3
        resolver.nameservers = forwarders

        try:
            result = resolver.query(qname=name,
                                    rdtype=self.question.rdtype,
                                    rdclass=self.question.rdclass,
                                    source=self.interface)

            address = result[0].address

            self.message += u'(dns.resolver). '

            logging.debug(u'Address for {name} via dns.resolver from nameservers - {source} '
                          u'on interface {interface}: {address}'.format(name=name,
                                                                        source=u', '.join(forwarders),
                                                                        interface=self.interface,
                                                                        address=address))

        except (IndexError, dns.exception.DNSException, dns.exception.Timeout, AttributeError) as err:
            self.message += u'(dns.resolver failed). '
            raise DNSQueryFailed(u'dns.resolver failed: {err}'.format(err=err))

        else:
            return result

    def _reply(self):

        packet = b''
        packet += self.data[:2] + b"\x81\x80"
        packet += self.data[4:6] + self.data[4:6] + b'\x00\x00\x00\x00'     # Questions and Answers Counts
        packet += self.data[12:]                                            # Original Domain Name Question
        packet += b'\xc0\x0c'                                               # Pointer to domain name
        packet += b'\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04'               # Response type, ttl and resource data length -> 4 bytes
        packet += self.ip.packed                                            # 4 bytes of IP

        return packet

    def _bad_reply(self):
            # TODO: Figure out how to return rcode 2 or 3
            # DNS Response Code | Meaning
            # ------------------+-----------------------------------------
            # RCODE:2           | Server failed to complete the DNS request
            # RCODE:3           | this code signifies that the domain name
            #                   | referenced in the query does not exist.
            logging.warning(self.error)
            # For now, return localhost,
            # which should fail on the calling machine
            self.ip = u'127.0.0.1'

            return self._reply()
