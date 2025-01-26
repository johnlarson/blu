import click

from blu._cli.utils import to_sync


@click.command()
@to_sync
async def dev():
    ...