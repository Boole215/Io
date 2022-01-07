from OpenSSL import crypto
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from dataclasses import dataclass
from socket import gethostname

@dataclass
class host_entry:
    fingerprint: bytes
    valid_range: tuple


trusted_certs = {}


def valid_cert(pem_cert, URL):
    # Get the certificate into a parseable medium and fingerprint
    cert = x509.load_pem_x509_certificate(str.encode(pem_cert), default_backend())
    fingerprint = cert.fingerprint(hashes.SHA256())

    if not URL in trusted_certs:
        trusted_certs[URL] = (fingerprint, (cert.not_valid_before, cert.not_valid_after))
        # Connection may proceed normally
        return True

    elif URL in trusted_certs and trusted_certs[URL][0] != fingerprint:
        # Cert is different, check if the cert is still valid
        cur_time = datetime.now(tz=timezone.utc)
        valid_range = trusted_certs[URL][1]
        if valid_range[0] <= cur_time and cur_time <= valid_range[1]:
            # Original cert is still valid, warn user and ask if they'd like to proceed
            return False

        else:
            # original cert is no longer valid, accept the new cert
            trusted_certs[URL] = host_entry(fingerprint, (cert.not_valid_before, cert.not_valid_after))
            return True

def generate_client_cert():
    # Generate Key Pair
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 1024)
    client_cert = crypto.X509()

    # Generate Self Signed Cert
    client_cert.get_subject().C = "TR"
    client_cert.get_subject().ST = "KAMINA"
    client_cert.get_subject().L = "KAMINA CITY"
    client_cert.get_subject().O = "LAGANN BROWSER LLC"
    client_cert.get_subject().OU = "LAGANN BROWSER LLC"
    client_cert.get_subject().CN = gethostname()
    client_cert.set_serial_number(1000)
    client_cert.gmtime_adj_notBefore(0)
    client_cert.gmtime_adj_notAfter(10*365*24*60*60)
    client_cert.set_issuer(client_cert.get_subject())
    client_cert.set_pubkey(key)
    client_cert.sign(key, 'sha1')

    # return client cert and key
    return (client_cert, key)
