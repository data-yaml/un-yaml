import logging

import pytest

logging.basicConfig(level=logging.DEBUG)
pytestmark = pytest.mark.anyio

TEST_URI = "doc+s3://fubar.com/foo/bar?baz=qux#frag=ment"
