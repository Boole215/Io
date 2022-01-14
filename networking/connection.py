import ssl, socket, select, logging
import networking.lagcerts as lagcerts

from networking.errors import InvalidHostError, MetaOverflowError
from networking.log import netlog

from datetime import datetime, timezone
from OpenSSL import crypto
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from dataclasses import dataclass

GEMINI_PORT = 1965

@dataclass
class Response:
    code: str
    MIME: str
    body: bytes


#TODO: open connection to the host, and ask for the particular page when making the request
#      e.g. open socket to host 'gemini.circumlunar.space'
#      but when making the request, request 'gemini://gemini.circumlunar.space/'
class Connection:

    def __init__(self, host, query, cert=None):
        # make connection
        context = ssl.SSLContext()
        self.host = host
        self.query = query

        try:
            netlog.debug("Attempting to connect to {}".format(self.host))
            connection = socket.create_connection((self.host, GEMINI_PORT), 10)
        except socket.error:
            netlog.debug("Invalid host, raising exception")
            raise InvalidHostError

        self.sock = context.wrap_socket(connection, server_hostname=self.host)
        der_cert = self.sock.getpeercert(True)
        pem_cert = ssl.DER_cert_to_PEM_cert(der_cert)


        if not lagcerts.valid_cert(pem_cert, self.host):
            self.maybe_unsafe = True
        else:
            self.maybe_unsafe = False



    def need_to_prompt(self):
        return self.maybe_unsafe



    def send_request(self, cert_needed = False):
        request = (self.query + '\r\n').encode('utf8')
        netlog.debug("sending request {}".format(request))
        self.sock.send(request)

    def receive_response(self):
        PACKET_SIZE = 2048

        ready = select.select([self.sock], [], [], 10)
        if ready[0]:

	    # TODO: headers and response body are not necessarily split into two different streams
            #       Accept the bare minimum # of bytes to get the MIME type, then check to see is
            #       a type is present. If not, then the MIME must be a response explanation.
            #       Try parsing based on b'\r\n' to get the end of the response headers.
            #       Check the docs again to be sure

            #headers = self.sock.recv(PACKET_SIZE)
            #netlog.debug(headers)


            #if len(headers) > 1024 + 5:
                #raise MetaOverflowError

            entirety = b''
            buf = b'ohnoo'

            while len(buf) != 0:
                buf = self.sock.recv(PACKET_SIZE)
                entirety += buf

            header_end = entirety.find(b'\r\n')

            if header_end > 1029:
                raise MetaOverflowError

            return Response(entirety[0:2], entirety[3:header_end], entirety[header_end+2:len(entirety)])

        netlog.debug("No answer received, ")
        self.close_connection()
        raise InvalidHostError


    def close_connection(self):
        self.sock.close()
