
import argparse
from typing import Protocol


class DevArgs(Protocol):
    pass


async def run(args: DevArgs):
    pass


def add_args(p: argparse.ArgumentParser):
    pass