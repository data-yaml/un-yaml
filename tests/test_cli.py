from io import StringIO

from un_yaml import UnCli

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

