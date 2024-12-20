import argparse
import asyncio
from importlib import import_module
import logging
from pathlib import Path
import sys
import os

log = logging.getLogger(__name__)

my_dir = Path(__file__).parent

SUBCOMMANDS = [
    'build',
    'dev',
]


def main():
    logging.basicConfig(level=logging.INFO)
    sys.path.append(os.getcwd())
    argv = sys.argv[1:]
    run(argv)


def run(argv: list[str]):
    args = _get_args(argv)
    asyncio.run(args.runner(args))


def _get_args(argv: list[str]):
    p = argparse.ArgumentParser()
    sp = p.add_subparsers()
    for cmd_name in SUBCOMMANDS:
        cmd_parser = sp.add_parser(cmd_name)
        cmd_module_path = f'.{cmd_name}'
        cmd_module = import_module(cmd_module_path, __name__)
        cmd_module.add_args(cmd_parser)
        cmd_parser.set_defaults(runner=cmd_module.run)
    return p.parse_args(argv)
