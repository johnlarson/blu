import os
import sys
import click

from blu._cli.build import build
from blu._cli.dev import dev


@click.group()
def cli():
    sys.path.append(os.getcwd())


cli.add_command(dev, name='dev')
cli.add_command(build, name='build')