from contextlib import nullcontext as does_not_raise

from un_yaml import UnCli, UnYaml

from .conftest import pytest, pytestmark  # NOQA F401


@pytest.fixture
def un():
    return UnCli()


def test_un_load():
    yaml_data = UnYaml.LoadYaml(UnCli.CLI_YAML, "tests")
    assert yaml_data
    assert UnYaml.KEY in yaml_data
    un = UnYaml(yaml_data)
    assert un


def test_un_new():
    un = UnYaml.New('app', 'doc')
    assert un
    assert un.info("app") == "app"
    assert un.info("doc") == "doc"


def test_un_init(un: UnYaml):
    assert UnYaml.KEY in un.data
    assert isinstance(un, UnYaml)


def test_un_info(un: UnYaml):
    assert "UnCli" == un.info("app")
    assert "un_yaml" == un.info("doc")


def test_un_expand(un: UnYaml):
    obj = {} # type: ignore
    assert obj == un.expand(obj)
    literal = {"key": "value"}
    assert literal == un.expand(literal)
    ref = {UnYaml.REF: "#/variables/uri"}
    assert un.data["variables"]["uri"] == un.expand(ref)


def test_un_get(un: UnYaml):
    assert un.get(UnYaml.KEY)
    assert not un.get("cmd/list")
    assert un.get("commands/list")
    assert un.get("commands/list/arguments")
    arg0 = un.get("commands/list/arguments/0")
    assert isinstance(arg0, dict)
    assert "uri" == arg0.get("name")


def test_un_re_expand(un: UnYaml):
    getref = un.get("commands/get")
    assert "help" in getref
    assert "arguments" in getref
    args = getref["arguments"]
    dir = args[0]
    assert "name" in dir
    assert dir["type"] == "Path"


def test_un_get_handler(un: UnYaml):
    for key in ["doc"]:
        with does_not_raise():
            un.get_handler(key)
    with pytest.raises(ValueError):
        un.get_handler("unknown")


def vd(k: str, val = None):
    return {k: val} if val else {k: f"val_{k}"}


def test_un_put():
    un: UnYaml = UnYaml.New("app", "doc")
    R1 = "root1"
    C1 = "child1"
    R2 = "root2"
    C2 = "child2"
    C3 = "child3"
    C4 = "child4"

    v1 = vd(C1)
    v0 = vd(R1, v1)
    assert v0
    assert v0[R1] == v1

    un.put(R1, v1)
    assert un.get(R1) == v1
    assert un.get(R1).get(C1) == v1[C1]

    v2 = vd(C2)
    un.put(R2, v2)
    assert un.get(R2) == v2


    k11 = R1 + UnYaml.SEP + C1
    v3 = vd(C3)
    un.put(k11, v3)
    assert un.get(k11) == v3
    assert un.get(R1).get(C1) == v3

    v4 = vd(C4)
    k14 = R1 + UnYaml.SEP + C4
    print('R1', un.data[R1])
    un.put(k14, v4[C4])
    print('R1', un.data[R1])
    assert un.get(R1).get(C1) == v3
    assert un.get(R1).get(C4) == v4[C4]
