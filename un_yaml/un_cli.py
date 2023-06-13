import logging
from argparse import ArgumentParser, Namespace
from collections.abc import Sequence
from pathlib import Path  # NOQA F401
from sys import stdout
from typing import Any

from .un_conf import UnConf
from .un_uri import UnUri
from .un_yaml import UnYaml

# Harcode most parameters for now
# TODO: infer them from the YAML file


class UnCli(UnYaml):
    """Use UnYaml to create a CLI from a YAML file."""

    CLI_YAML = "cli.yaml"
    ARG_KEYS = (
        "dest,metavar,type,default,required,choices,action,nargs,const,help".split(",")
    )
    K_ARG = "argument"
    K_CMD = "command"
    K_OPT = "option"
    K_VER = "version"
    K_VRB = "verbose"
    K_GLOB = "global"

    @staticmethod
    def VALID_KEYS(arg: dict):
        kwargs = {k: v for k, v in arg.items() if k in UnCli.ARG_KEYS}
        if "type" in kwargs:
            kwargs["type"] = eval(kwargs["type"])
        return kwargs

    def __init__(self, pkg: str, version: str, file=CLI_YAML, dir=".") -> None:
        yaml_data = UnYaml.LoadYaml(file, pkg)
        super().__init__(yaml_data)
        if UnCli.K_CMD not in self.data:
            raise ValueError(f"'{UnCli.K_CMD}' not in file '{file}':\n{self.data}")
        self.version = version
        self.cmds = self.get(UnCli.K_CMD)
        self.doc = self.get_handler("doc")()
        self.path = Path(dir) / UnCli.DEFAULT
        self.conf = UnConf(self.path, doc=type(self.doc).__name__)

    def parse_version(self, parser: ArgumentParser) -> None:
        doc_name = self.info("doc")
        parser.add_argument(
            "-V",
            f"--{UnCli.K_VER}",
            action="store_const",
            const=f"{doc_name} {self.version}",
            help="Show version and exit.",
        )

    def make_parser(self) -> ArgumentParser:
        parser = ArgumentParser(self.info("doc"))
        self.parse_version(parser)
        subparsers = parser.add_subparsers(dest=UnCli.K_CMD)
        for cmd, opts in self.cmds.items():
            if cmd[0] != "_":
                subparser = subparsers.add_parser(cmd, help=opts["help"])
                for arg in opts.get(UnCli.K_ARG, []):
                    subparser.add_argument(arg["name"], **UnCli.VALID_KEYS(arg))
                for opt in opts.get(UnCli.K_OPT, []):
                    subparser.add_argument(
                        opt["short"], opt["name"], **UnCli.VALID_KEYS(opt)
                    )
                globs = self.get(UnCli.K_GLOB) or {}
                for gopts in globs.values():
                    nopts: list[str] = [gopts.get("short"), gopts.get("name")]
                    names = filter(None, nopts)
                    subparser.add_argument(*names, **UnCli.VALID_KEYS(gopts))
        return parser

    async def run(self, argv: Sequence[str] | None, out=stdout):
        args = self.parse(argv)
        if not args:
            return False
        if hasattr(args, UnCli.K_VER) and args.version:
            print(args.version, file=out)
            return False
        if hasattr(args, UnCli.K_VRB) and args.verbose:
            logging.basicConfig()
            logging.getLogger().setLevel(logging.DEBUG)
        return await self.execute(args, out)

    def parse(self, argv: Sequence[str] | None) -> Namespace | None:
        parser = self.make_parser()
        args = parser.parse_args(argv)
        logging.debug(f"UnCli.parse.args: {args}")
        if args.command is None and not args.version:
            parser.print_help()
            return None
        return args

    def get_resource(self, uri: UnUri) -> Any:
        handler = self.get_handler(uri.tool())
        logging.debug(f"get_resource.handler: {handler}")
        return handler(uri.attrs)

    def log_resource(self, argv: dict):
        args = argv.copy()
        args[UnCli.K_VER] = self.version
        uri = args.pop(UnUri.ARG_URI)
        tool = uri.tool()
        opts = {str(uri): args}
        logging.debug(f"tool[{tool}] {opts}")
        self.conf.put(tool, opts)
        self.conf.save()

    def resource(self, argv: dict) -> dict:
        """Hardcode resource transformation to key named URI, for now"""
        if UnUri.ARG_URI in argv:
            uri = argv[UnUri.ARG_URI]
            self.log_resource(argv)
            argv[UnUri.ARG_RESOURCE] = self.get_resource(uri)
        return argv

    async def execute(self, args: Namespace, out=stdout):
        """Invoke Appropriate Command."""
        cmd = args.command
        if cmd not in self.cmds:
            logging.error(f"Unknown command: {cmd}\n{args}")
            exit(1)

        argv = vars(args)
        self.resource(argv)
        logging.debug(f"UnCli.execute.argv: {argv}")

        results = await self.doc.execute(cmd, argv)
        return self.echo(results, out)

    def echo(self, results: list, out=stdout):
        """Print result of calling a method."""
        [print(f'"{item}"', file=out) for item in results]
        return out
