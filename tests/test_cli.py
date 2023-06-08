import sys
from argparse import Namespace
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from un_yaml import UnCli, UnUri, __version__

from .conftest import SRC_PACKAGE, TEST_URI, pytest, pytestmark  # NOQA F401


@pytest.fixture
def cli():
    return UnCli(SRC_PACKAGE, __version__)


@pytest.fixture
def buf():
    result = StringIO()
    yield result
    result.close()


def test_cli(cli: UnCli):
    assert cli
    commands = cli.get(UnCli.K_CMD)
    assert commands
    assert "list" in commands


def test_cli_arg():
    d = {"type": "Path"}
    kw = UnCli.VALID_KEYS(d)
    assert kw


async def test_cli_parser(cli: UnCli, buf: StringIO):
    argv = ["--version"]
    parser = cli.make_parser()
    assert parser
    assert cli.parse(argv)
    await cli.run(argv, buf)
    assert "un_yaml" in buf.getvalue()


def test_cli_parse_arg(cli: UnCli):
    argv = ["list", TEST_URI]
    names = cli.parse(argv)
    assert isinstance(names, Namespace)
    assert names.command == "list"
    uri = names.uri
    assert isinstance(uri, UnUri)
    assert str(uri) == TEST_URI


def test_cli_parse_opt(cli: UnCli):
    argv = ["get", TEST_URI]  # , "--dir", "."
    names = cli.parse(argv)
    assert isinstance(names, Namespace)
    assert names.command == "get"
    assert hasattr(names, "dir")
    assert names.dir == Path(".")
    assert not names.verbose


async def test_cli_verbose(cli: UnCli, buf: StringIO):
    argv = ["get", TEST_URI, "--verbose"]  # , "--dir", "."
    names = cli.parse(argv)
    assert isinstance(names, Namespace)
    assert names.verbose


async def test_cli_run(cli: UnCli, buf: StringIO):
    # assert not await cli.run(None, buf) FAILS when using pytest arguments
    assert not await cli.run([], buf)
    await cli.run(["list", TEST_URI], buf)
    assert "list" in buf.getvalue()
    doc_opts = cli.conf.get("doc")
    assert doc_opts
    uri_opts = doc_opts.get(TEST_URI)
    assert uri_opts
    assert uri_opts.get(UnCli.K_CMD) == "list"


@pytest.mark.skipif(sys.platform.startswith("win"), reason="tmp folder name issue")
def test_cli_conf():
    uri = UnUri(TEST_URI)
    tool = uri.tool()
    argv = {
        UnUri.ARG_URI: uri,
        "name": "test",
        UnCli.K_CMD: "list",
    }
    with TemporaryDirectory() as tmpdir:
        cli = UnCli(pkg=SRC_PACKAGE, dir=tmpdir, version=__version__)
        cf = cli.conf
        assert cf
        assert tmpdir in str(cli.path)
        assert tmpdir in str(cf.path)
        assert "Wrapper" == cf.info("doc")
        assert not cf.get(tool)

        assert not cli.path.exists()
        cli.log_resource(argv)
        assert cli.path.exists()

        contents = cli.path.read_text()
        assert "name: test" in contents

        opts = cf.get(tool)
        assert opts
        args = opts.get(TEST_URI)
        assert args
        assert args["name"] == "test"
        assert args.get(UnUri.ARG_URI, False) is False
        assert args.get(UnCli.K_CMD) == "list"
