import os
import click

from blu._app import Blu
from blu._utils.asyncio import syncify


@click.command()
@syncify
async def build():
    await Blu('app', os.getcwd()).build()