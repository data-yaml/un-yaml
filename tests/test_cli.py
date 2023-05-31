from io import StringIO
from pathlib import Path

from un_yaml import UnCli, UnUri

from .conftest import pytest, pytestmark  # NOQA F401


@pytest.fixture
def cli():
    return UnCli()


@pytest.fixture
def buf():
    result = StringIO()
    yield result
    result.close()


def test_un_cli(cli: UnCli):
    assert cli
    commands = cli.get(UnCli.CMD)
    assert commands
    assert "list" in commands


def test_un_cli_eval():
    assert eval("str") == str
    assert eval("Path") == Path
    assert eval("UnUri") == UnUri


def test_un_cli_arg():
    d = {"type": "Path"}
    kw = UnCli.ARG_KWS(d)
    assert kw


async def test_un_cli_parser(cli: UnCli, buf: StringIO):
    argv = ["--version"]
    parser = cli.make_parser()
    assert parser
    assert cli.parse(argv)
    await cli.run(argv, buf)
    assert "un_yaml" in buf.getvalue()
