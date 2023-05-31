from un_yaml import UnUri

from .conftest import pytest, pytestmark  # NOQA F401


async def test_uri():
    uri = UnUri("quilt+s3://quilt-example")
    assert uri
    assert "quilt" == uri.tool()
    assert "s3" == uri.get("_protocol")
    assert "s3://quilt-example" == uri.endpoint()
