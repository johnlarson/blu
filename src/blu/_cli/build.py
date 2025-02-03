import os
import click

from blu._app import Blu
from blu._utils.asyncio import to_sync


@click.command()
@to_sync
async def build():
    await Blu('app', os.getcwd()).build()