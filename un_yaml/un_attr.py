# Parse a UDC "app+protocol://" URI
from typing_extensions import Any


class UnAttr:
    ARG_URI = "uri"
    ARG_RESOURCE = "resource"
    SEP = "+"

    K_HOST = "_hostname"
    K_ID = "_id"
    K_PROT = "_protocol"
    K_QRY = "_query"
    K_TOOL = "_tool"
    K_UPTH = "_uri_paths"
    K_URI = "_uri"

    def __init__(self, attrs: dict[str, Any]):
        """
        Store attributes by key
        """
        self.attrs = attrs

    def __repr__(self):
        return f"{self.__class__.__name__}({self.attrs})"
