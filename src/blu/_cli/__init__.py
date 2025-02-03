import click

from blu._cli.build import build
from blu._cli.dev import dev


@click.group()
def cli():
    pass


cli.add_command(dev, name='dev')
cli.add_command(build, name='build')