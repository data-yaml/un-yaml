from contextlib import nullcontext as does_not_raise

from un_yaml import UnCli, UnYaml, __version__

from .conftest import SRC_PACKAGE, pytest, pytestmark  # NOQA F401


@pytest.fixture
def un():
    return UnCli(SRC_PACKAGE, __version__)


def test_yaml_load():
    yaml_data = UnYaml.LoadYaml(UnCli.CLI_YAML, SRC_PACKAGE)
    assert yaml_data
    assert UnYaml.KEY in yaml_data
    un = UnYaml(yaml_data)
    assert un


def test_yaml_init(un: UnYaml):
    assert UnYaml.KEY in un.data
    assert isinstance(un, UnYaml)


def test_yaml_info(un: UnYaml):
    assert "UnCli" == un.info("app")
    assert "un_yaml" == un.info("doc")


def test_yaml_expand(un: UnYaml):
    obj = {}  # type: ignore
    assert obj == un.expand(obj)
    literal = {"key": "value"}
    assert literal == un.expand(literal)
    ref = {UnYaml.REF: "#/variable/uri"}
    assert un.data["variable"]["uri"] == un.expand(ref)


def test_yaml_get(un: UnYaml):
    assert un.get(UnYaml.KEY)
    assert not un.get("cmd/list")
    assert un.get("command/list")
    assert un.get("command/list/argument")
    arg0 = un.get("command/list/argument/0")
    assert isinstance(arg0, dict)
    assert "uri" == arg0.get("name")


def test_yaml_re_expand(un: UnYaml):
    getref = un.get("command/get")
    assert "help" in getref
    assert "argument" in getref
    args = getref["argument"]
    uri_opts = args[0]
    assert "name" in uri_opts
    assert uri_opts["name"] == "uri"
    assert uri_opts["type"] == "UnUri"


def test_yaml_get_handler(un: UnYaml):
    for key in ["doc"]:
        with does_not_raise():
            un.get_handler(key)
    with pytest.raises(ValueError):
        un.get_handler("unknown")
