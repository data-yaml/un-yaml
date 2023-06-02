from yaml import representer

from .un_cli import UnCli  # NOQA F401
from .un_conf import UnConf  # NOQA F401
from .un_uri import UnUri  # NOQA F401
from .un_yaml import UnYaml  # NOQA F401

def default_representer(dumper, data):
    # Alternatively, use repr() instead of str():
    return dumper.represent_scalar("tag:yaml.org,2002:str", str(data))

representer.SafeRepresenter.add_representer(None, default_representer) # type: ignore
