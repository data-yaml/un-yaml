import logging

import pytest

logging.basicConfig(level=logging.DEBUG)
pytestmark = pytest.mark.anyio

SRC_PACKAGE = "un_yaml"

TEST_URI = "doc+s3://fubar.com/foo/bar?baz=qux#frag=ment"
