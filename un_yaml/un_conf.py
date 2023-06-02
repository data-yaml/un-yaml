import logging
from pathlib import Path  # NOQA F401
from typing import Any

from yaml import safe_dump, safe_load

from .un_cli import __version__
from .un_yaml import UnYaml


class UnConf(UnYaml):
    """Editable subclass of UnYaml."""

    DEFAULT = "data.yaml"
    DEFAULT_INFO = {
        "_version": __version__,
        "app": "data-yaml",
        "app_version": "0.0.1",
        "doc": __name__,
        "doc_version": "0.0.1",
    }

    @staticmethod
    def SaveYaml(path: Path, yaml_data: dict):
        with path.open("w") as outfile:
            safe_dump(yaml_data, outfile)

    @staticmethod
    def ReadYaml(path: Path, defaults={}) -> dict:
        if not path.exists():
            return UnConf.NewYaml(defaults)
        yaml_string = path.read_text()
        yaml_data = safe_load(yaml_string)

        if not yaml_data:
            return UnConf.NewYaml(defaults)
        return yaml_data

    @classmethod
    def NewYaml(cls, info={}) -> dict:
        opts = UnConf.DEFAULT_INFO | {"doc": cls.__name__} | info
        yaml_data = {UnConf.KEY: opts}
        return yaml_data

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
