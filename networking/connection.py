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

    def __init__(self, URL, cert=None):
        # make connection
        context = ssl.SSLContext()
        self.host, self.query = self._parse_query(URL)

        try:
            netlog.debug("Attempting to connect to {}".format(self.host))
            connection = socket.create_connection((self.host, GEMINI_PORT), 10)
        except socket.error:
            netlog.debug("Invalid host, raising exception")
            raise InvalidHostError

        self.sock = context.wrap_socket(connection)
        der_cert = self.sock.getpeercert(True)
        pem_cert = ssl.DER_cert_to_PEM_cert(der_cert)


        if not lagcerts.valid_cert(pem_cert, URL):
            self.maybe_unsafe = True
        else:
            self.maybe_unsafe = False



    def _parse_query(self, query):
        GEM_LEN = 9
        if "gemini://" not in query:
            query = "gemini://" + query

        page = query[GEM_LEN:].find("/")

        if page == -1:
            host = query[GEM_LEN:]
            query = query + "/"
        else:
            host = query[GEM_LEN:page+GEM_LEN]

        return (host, query)



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
            headers = self.sock.recv(PACKET_SIZE)
            if len(headers) > 1024 + 5:
                raise MetaOverflowError
            body = b''
            buf = b'ohnoo'

            while len(buf) != 0:
                buf = self.sock.recv(PACKET_SIZE)
                body += buf


            return Response(headers[0:2], headers[3:len(headers)-2], body)


        netlog.debug("No answer received, ")
        self.close_connection()
        raise InvalidHostError


    def close_connection(self):
        self.sock.close()
