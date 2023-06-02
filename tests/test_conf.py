from un_yaml import UnConf

from .conftest import pytest, pytestmark  # NOQA F401
from tempfile import TemporaryDirectory
from pathlib import Path

@pytest.fixture
def un():
    with TemporaryDirectory() as tmpdirname:
        path = Path(tmpdirname) / UnConf.DEFAULT
        yield UnConf(path, app="app", doc="doc")

def test_conf_new(un: UnConf):
    assert un
    assert un.info("app") == "app"
    assert un.info("doc") == "doc"


def test_conf_default():
    with TemporaryDirectory() as tmpdirname:
        path = Path(tmpdirname) / UnConf.DEFAULT
        un = UnConf(path)
        assert un.info("app") == "data-yaml"
        assert un.info("doc") == "UnConf"

def test_conf_save():
    test_dict = {"a": 1, "b": 2}
    with TemporaryDirectory() as tmpdirname:
        path = Path(tmpdirname) / "test1.yaml"
        un1 = UnConf(path, **test_dict)
        assert un1.info("a") == 1
        un1.put("c", 3)
        un1.save()
        
        un1.put("c", 4)
        un2 = UnConf(path)
        assert un2.get("c") == 3
        assert un2.data != un1.data

        assert un1.get("c") == 4
        un1.reload()
        assert un1.get("c") == 3
        assert un2.data == un1.data


def vd(k: str, val = None):
    return {k: val} if val else {k: f"val_{k}"}


def test_conf_put(un: UnConf):
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


    k11 = R1 + UnConf.SEP + C1
    v3 = vd(C3)
    un.put(k11, v3)
    assert un.get(k11) == v3
    assert un.get(R1).get(C1) == v3

    v4 = vd(C4)
    k14 = R1 + UnConf.SEP + C4
    print('R1', un.data[R1])
    un.put(k14, v4[C4])
    print('R1', un.data[R1])
    assert un.get(R1).get(C1) == v3
    assert un.get(R1).get(C4) == v4[C4]
