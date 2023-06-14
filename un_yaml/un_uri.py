# Parse a UDC "app+protocol://" URI

from json import loads
from typing import Any
from urllib.parse import parse_qs, urlparse

from .un_attr import UnAttr


class UnUri(UnAttr):
    @staticmethod
    def ExtractJson(result):
        if not isinstance(result, str) or result[0] != "{":
            return result
        if "'" in result:
            result = result.replace("'", '"')  # JSON parser requires double quotes
        return loads(result)

    @staticmethod
    def NormalizeQuery(query: dict) -> dict:
        for key, value in query.items():
            if isinstance(value, list):  # non-parsed
                query[key] = UnUri.ExtractJson(value[0])
        return query

    def __init__(self, uri_string: str):
        """
        Parse a UDC "app+protocol://" URI into components
        - parse fragment into `attrs`
        - use special attr keys for other components

        >>> uri = UnUri("udc+http://example.com?key=value#foo=bar&fubar=baz")
        >>> uri.attrs[UnUri.K_HOST]
        'example.com'
        >>> uri.attrs[UnUri.K_PROT]
        'http'
        >>> uri.attrs[UnUri.K_QRY]
        {'key': 'value'}
        >>> uri.attrs['foo']
        'bar'
        >>> uri.attrs[UnUri.K_TOOL]
        'udc'
        >>> uri.attrs[UnUri.K_URI]
        'udc+http://example.com?key=value#foo=bar&fubar=baz'
        >>> uri.attrs.get(UnUri.K_ID)
        'bar'

        """
        self.uri = urlparse(uri_string)
        attrs = self.parse_query(self.uri.fragment)
        super().__init__(attrs)
        frags = attrs.values()
        self.parse_scheme(self.uri.scheme)
        self.attrs[UnUri.K_ID] = next(iter(frags), self.attrs[UnUri.K_TOOL])
        self.attrs[UnUri.K_HOST] = self.uri.hostname or "localhost"
        self.attrs[UnUri.K_UPTH] = self.uri.path.strip("/").split("/")
        self.attrs[UnUri.K_QRY] = self.parse_query(self.uri.query)
        self.attrs[UnUri.K_URI] = uri_string

    def __repr__(self):
        return f"UnUri({self.attrs[UnUri.K_URI]})"

    def __str__(self):
        return self.attrs[UnUri.K_URI]

    def get(self, key):
        return self.attrs.get(key)

    def parse_query(self, query: str) -> dict[str, Any]:
        list_dict = parse_qs(query)
        scalars = {k: v[0] for k, v in list_dict.items()}
        return UnUri.NormalizeQuery(scalars)

    def parse_scheme(self, scheme: str):
        schemes = scheme.split(UnUri.SEP)
        if len(schemes) != 2:
            raise ValueError(
                f"Error: URI scheme `{self.uri.scheme}` does not contain '{UnUri.SEP}'"
            )
        self.attrs[UnUri.K_TOOL] = schemes[0]
        self.attrs[UnUri.K_PROT] = schemes[1]

    def tool(self):
        return self.attrs[UnUri.K_TOOL]

    def endpoint(self):
        return f"{self.attrs[UnUri.K_PROT]}://{self.attrs[UnUri.K_HOST]}"
