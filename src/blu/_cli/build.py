
import argparse
from typing import Protocol


class BuildArgs(Protocol):
    pass


async def run(args: BuildArgs):
    pass


def add_args(p: argparse.ArgumentParser):
    pass