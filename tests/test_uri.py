from un_yaml import UnUri

from .conftest import pytest, pytestmark  # NOQA F401


async def test_uri():
    uri = UnUri("quilt+s3://quilt-example")
    assert uri
    assert "quilt" == uri.tool()
    assert "s3" == uri.get("_protocol")
    assert "s3://quilt-example" == uri.endpoint()

async def test_uri_keys():
    TEST_URI = "quilt+s3://fubar.com/foo/bar?baz=qux#frag=ment"
    uri = UnUri(TEST_URI)
    a = uri.attrs
    assert a
    assert a[UnUri.K_TOOL] == "quilt"
    assert a[UnUri.K_PROT] == "s3"
    assert a[UnUri.K_HOST] == "fubar.com"
    assert a[UnUri.K_UPTH] == ["foo", "bar"]
    assert a[UnUri.K_QRY] == {"baz": "qux"}
    assert a[UnUri.K_URI] == TEST_URI
