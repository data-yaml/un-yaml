import sys
from io import StringIO
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
    commands = cli.get(UnCli.CMDS)
    assert commands
    assert "list" in commands


def test_cli_arg():
    d = {"type": "Path"}
    kw = UnCli.ARG_KWS(d)
    assert kw


async def test_cli_parser(cli: UnCli, buf: StringIO):
    argv = ["--version"]
    parser = cli.make_parser()
    assert parser
    assert cli.parse(argv)
    await cli.run(argv, buf)
    assert "un_yaml" in buf.getvalue()


async def test_cli_run(cli: UnCli, buf: StringIO):
    # assert not await cli.run(None, buf) FAILS when using pytest arguments
    assert not await cli.run([], buf)
    await cli.run(["list", TEST_URI], buf)
    assert "list" in buf.getvalue()
    doc_opts = cli.conf.get('doc')
    assert doc_opts
    uri_opts = doc_opts.get(TEST_URI)
    assert uri_opts
    assert uri_opts.get(UnCli.CMD) == "list"


@pytest.mark.skipif(sys.platform.startswith('win'), reason="tmp folder name issue")
def test_cli_conf():
    uri = UnUri(TEST_URI)
    tool = uri.tool()
    argv = {
        UnUri.ARG_URI: uri,
        "name": "test",
        UnCli.CMD: "list",
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
        assert args.get(UnUri.ARG_URI, False) == False
        assert args.get(UnCli.CMD) == "list"
