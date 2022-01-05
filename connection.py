import ssl, socket, lagcerts
from datetime import datetime, timezone
from OpenSSL import crypto
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from dataclasses import dataclass

GEMINI_PORT = 1965

@dataclass
class Response:
    code: int
    MIME: str
    body: bytes



class Connection:
    def __init__(self, URL, cert=None):
        # make connection
        context = ssl.SSLContext()
        connection = socket.create_connection((URL, GEMINI_PORT))
        self.host = URL
        self.sock = context.wrap_socket(connection)
        der_cert = self.sock.getpeercert(True)
        pem_cert = ssl.DER_cert_to_PEM_cert(der_cert)

        if not lagcerts.valid_cert(pem_cert, URL):
            self.maybe_unsafe = True
        else:
            self.maybe_unsafe = False


    def need_to_prompt(self):
        return self.maybe_unsafe



    def send_request(self, cert_needed = False):
        if "gemini://" not in self.host:
            request = ("gemini://"+self.host+'/\r\n').encode('utf8')
        else:
            request = (self.host+'/\r\n').encode('utf8')

        self.sock.send(request)

    def receive_response(self):
        PACKET_SIZE = 2048
        headers = self.sock.recv(PACKET_SIZE)
        print(headers)
        print("I am in receive_response")
        body = b''
        buf = b'ohnoo'

        while len(buf) != 0:
            buf = self.sock.recv(PACKET_SIZE)
            body += buf

        return Response(headers[0:2], headers[3:len(headers)-2], body)

    def close_connection(self):
        self.sock.close()
