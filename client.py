import ssl, socket
from datetime import datetime, timezone
from OpenSSL import crypto
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes

trusted_certs = {}



class Client:

    # Initialize as false
    client_cert = False
    cur_page = ""

    def connect_to_server(self, URL):
        context = ssl.SSLContext()
        connection = socket.create_connection((URL, 1965))
        self.host = URL
        self.sock = context.wrap_socket(connection)
        print(self.valid_cert(URL),'\n')


    def send_request(self):
        request = ("gemini://"+self.host+'/\r\n').encode('utf8')
        self.sock.send(request)

    def receive_response(self):
        PACKET_SIZE = 1024
        complete = b''
        buf = b'ohnoo'
        while len(buf) != 0:
            buf = self.sock.recv(PACKET_SIZE)
            complete += buf
            print(buf)




    def valid_cert(self, URL):
        der_cert = self.sock.getpeercert(True)
        pem_cert = ssl.DER_cert_to_PEM_cert(der_cert)
        # Get the certificate into a parseable medium and fingerprint
        cert = x509.load_pem_x509_certificate(str.encode(pem_cert), default_backend())
        fingerprint = cert.fingerprint(hashes.SHA256())

        if not URL in trusted_certs:
            trusted_certs[URL] = (fingerprint, (cert.not_valid_before, cert.not_valid_after))
            # Connection may proceed normally
            return 1

        elif URL in trusted_certs and trusted_certs[URL][0] != fingerprint:
            # Cert is different, check if the cert is still valid
            cur_time = datetime.now(tz=timezone.utc)
            valid_range = trusted_certs[URL][1]
            if valid_range[0] <= cur_time and cur_time <= valid_range[1]:
                # Original cert is still valid, warn user and ask if they'd like to proceed
                return 0

            else:
                # original cert is no longer valid, accept the new cert
                trusted_certs[URL] = (fingerprint, (cert.not_valid_before, cert.not_valid_after))
                return 1

    def generate_client_cert(self):
        # Generate Key Pair
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 1024)
        client_cert = crypto.X509()

        # Generate Self Signed Cert
        client_cert.get_subject().C = "COUNTRY"
        client_cert.get_subject().ST = "STATE"
        client_cert.get_subject().L = "LOCALITY"
        client_cert.get_subject().O = "APOLLO BROWSER LLC"
        client_cert.get_subject().OU = "APOLLO BROWSER LLC"
        client_cert.get_subject().CN = socket.gethostname()
        client_cert.set_serial_number(1000)
        client_cert.gmtime_adj_notBefore(0)
        client_cert.gmtime_adj_notAfter(10*365*24*60*60)
        client_cert.set_issuer(client_cert.get_subject())
        client_cert.set_pubkey(key)
        client_cert.sign(key, 'sha1')

        # store client cert and key
        self.client_cert = client_cert
        self.key = key

    def save_certs(self):
        # perform pickling here
        return



my_client = Client()
my_client.connect_to_server("gemini.circumlunar.space")
my_client.send_request()
my_client.receive_response()
