from io import StringIO
from tempfile import TemporaryDirectory
from un_yaml import UnCli, UnUri, UnConf

from .conftest import pytest, pytestmark, TEST_URI  # NOQA F401


@pytest.fixture
def cli():
    return UnCli()


@pytest.fixture
def buf():
    result = StringIO()
    yield result
    result.close()


def test_cli(cli: UnCli):
    assert cli
    commands = cli.get(UnCli.CMD)
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

def test_cli_conf():
    uri = UnUri(TEST_URI)
    tool = uri.tool()
    argv = {
       UnUri.ARG_URI: uri,
       "name": "test",       
    }
    with TemporaryDirectory() as tmpdir:
        cli = UnCli(dir=tmpdir)
        cf = cli.conf
        assert cf
        assert tmpdir in str(cli.path)
        assert cli.doc == cf.info("doc")
        assert not cf.get(tool)

        assert not cli.path.exists()
        cli.log_resource(argv)
        opts = cf.get(tool)
        assert opts
        print(opts)
        args = opts.get(TEST_URI)
        assert args
        assert args["name"] == "test"



