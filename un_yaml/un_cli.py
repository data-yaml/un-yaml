import logging
from argparse import ArgumentParser, Namespace
from collections.abc import Sequence
from pathlib import Path  # NOQA F401
from sys import stdout
from typing import Any


from .un_conf import UnConf
from .un_uri import UnUri
from .un_yaml import UnYaml, __version__

# Harcode most parameters for now
# TODO: infer them from the YAML file


class UnCli(UnYaml):
    """Use UnYaml to create a CLI from a YAML file."""

    CLI_YAML = "cli.yaml"
    CMD = "commands"
    ARG_KEYS = (
        "dest,metavar,type,default,required,choices,action,nargs,const,help".split(",")
    )
    K_VER = "version"

    @staticmethod
    def ARG_KWS(arg: dict):
        kwargs = {k: v for k, v in arg.items() if k in UnCli.ARG_KEYS}
        kwargs["type"] = eval(kwargs["type"]) if "type" in kwargs else str
        return kwargs

    def __init__(self, pkg: str, file=CLI_YAML, dir=".") -> None:
        yaml_data = UnYaml.LoadYaml(file, pkg)
        super().__init__(yaml_data)
        if UnCli.CMD not in self.data:
            raise ValueError(f"'{UnCli.CMD}' not in file '{file}':\n{self.data}")
        self.cmds = self.get(UnCli.CMD)
        self.doc = self.get_handler("doc")()
        self.path = Path(dir) / UnCli.DEFAULT
        self.conf = UnConf(self.path, doc=type(self.doc).__name__)

    def parse_version(self, parser: ArgumentParser) -> None:
        doc_name = self.info("doc")
        parser.add_argument(
            "-v",
            f"--{UnCli.K_VER}",
            action="store_const",
            const=f"{doc_name} {__version__}",
            help="Show version and exit.",
        )

    def make_parser(self) -> ArgumentParser:
        parser = ArgumentParser(self.get("doc"))
        self.parse_version(parser)
        subparsers = parser.add_subparsers(dest="command")
        for cmd, opts in self.cmds.items():
            if cmd[0] != "_":
                subparser = subparsers.add_parser(cmd, help=opts["help"])
                args = opts.get("arguments")
                for arg in args or []:
                    subparser.add_argument(arg["name"], **UnCli.ARG_KWS(arg))
        return parser

    async def run(self, argv: Sequence[str] | None, out=stdout):
        args: Any = self.parse(argv)
        if not args:
            return False
        if hasattr(args, UnCli.K_VER) and args.version:
            print(args.version, file=out)
            return False
        return await self.execute(args, out)

    def parse(self, argv: Sequence[str] | None) -> Namespace | None:
        parser = self.make_parser()
        args = parser.parse_args(argv)
        if args.command is None and not args.version:
            parser.print_help()
            return None
        return args

    def get_resource(self, uri: UnUri) -> Any:
        handler = self.get_handler(uri.tool())
        logging.debug(f"handler: {handler}")
        return handler(uri.attrs)

    def log_resource(self, argv: dict):
        args = argv.copy()
        args.pop(UnCli.K_VER, None)
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

        results = await self.doc.execute(cmd, argv)
        return self.echo(results, out)

    def echo(self, results: list, out=stdout):
        """Print result of calling a method."""
        [print(f'"{item}"', file=out) for item in results]
        return out
