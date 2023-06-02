from un_yaml import UnUri

from .conftest import pytest, pytestmark  # NOQA F401


async def test_uri():
    TEST_URI = "quilt+s3://quilt-example"
    uri = UnUri(TEST_URI)
    assert uri
    assert "quilt" == uri.tool()
    assert "s3" == uri.get("_protocol")
    assert "s3://quilt-example" == uri.endpoint()
    assert TEST_URI in str(uri)


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


async def test_uri_query():
    TEST_QUERY: dict = {"name": ["foo"], "fields": ["{'bar':'baz'}"]}
    q = UnUri.NormalizeQuery(TEST_QUERY)
    assert q["name"] == "foo"
    assert "'bar'" not in q["fields"]
