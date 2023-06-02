import logging
from importlib.metadata import version
from pathlib import Path  # NOQA F401
from typing import Any
from yaml import safe_dump, safe_load

from .un_yaml import UnYaml

class UnConf(UnYaml):
    """Editable subclass of UnYaml."""
    DEFAULT= "data.yaml"

    @staticmethod
    def SaveYaml(path: Path, yaml_data: dict):
        with path.open('w') as outfile:
            safe_dump(yaml_data, outfile)

    @staticmethod
    def NewYaml(info={}) -> dict:
        yaml_data = {UnConf.KEY: info}
        return yaml_data

    @staticmethod
    def ReadYaml(path: Path) -> dict:
        yaml_string = path.read_text()
        yaml_data = safe_load(yaml_string)
        return yaml_data

    def __init__(self, path: Path, **defaults) -> None:
        yaml_data = UnConf.ReadYaml(path) if path.exists() else UnConf.NewYaml(defaults)
        super().__init__(yaml_data)
        self.path = path
    
    def put(self, keylist: str, value: Any):
        keys = keylist.split(UnConf.SEP)
        tail = keys.pop()

        parent = self.data
        for child in keys:
            logging.debug(f"child: {child} parent: {parent}")
            parent = parent[child]
            logging.debug(f"+parent: {parent}")
        parent[tail] = value

