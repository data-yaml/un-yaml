import logging
from pathlib import Path  # NOQA F401
from typing import Any

from yaml import safe_dump, safe_load

from .un_yaml import __version__
from .un_yaml import UnYaml


class UnConf(UnYaml):
    """Editable subclass of UnYaml."""

    @staticmethod
    def SaveYaml(path: Path, yaml_data: dict):
        with path.open("w") as outfile:
            safe_dump(yaml_data, outfile)


    def __init__(self, path: Path, **defaults) -> None:
        yaml_data = UnConf.ReadYaml(path.resolve(), defaults)
        super().__init__(yaml_data)
        self.path = path.resolve()

    def save(self):
        UnConf.SaveYaml(self.path, self.data)

    def reload(self):
        self.data = UnConf.ReadYaml(self.path)

    def put(self, keylist: str, value: Any):
        keys = keylist.split(UnConf.SEP)
        tail = keys.pop()

        parent = self.data
        for child in keys:
            logging.debug(f"child: {child} parent: {parent}")
            parent = parent[child]
            logging.debug(f"+parent: {parent}")
        parent[tail] = value
