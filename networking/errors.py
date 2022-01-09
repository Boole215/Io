
class InvalidHostError(Exception):
    """Raised when socket cannot connect to host"""
    pass

class MetaOverflowError(Exception):
    """
    Raised when the META field of a server's response
    exceeds 1024 bytes
    """
    pass
